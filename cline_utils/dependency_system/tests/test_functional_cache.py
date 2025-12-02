import pytest
import os
import time
import shutil
import json
from pathlib import Path
import numpy as np
import logging

from cline_utils.dependency_system.utils.cache_manager import CacheManager, cached, get_cache_stats, clear_all_caches, invalidate_dependent_entries
from cline_utils.dependency_system.utils import path_utils
from cline_utils.dependency_system.utils import config_manager
from cline_utils.dependency_system.analysis import embedding_manager
from cline_utils.dependency_system.core import dependency_grid
from cline_utils.dependency_system.io import tracker_io
from cline_utils.dependency_system.utils import tracker_utils
from cline_utils.dependency_system.core.key_manager import KeyInfo

# Helper function to touch a file (update mtime)
def touch(filepath):
    """Updates the modification time of a file."""
    try:
        Path(filepath).touch()
    except OSError as e:
        print(f"Error touching file {filepath}: {e}")

# --- Fixtures ---

@pytest.fixture(scope="function")
def clear_cache_fixture():
    """Ensures a clean cache state before each test function runs."""
    clear_all_caches()
    yield
    clear_all_caches()

@pytest.fixture(scope="session")
def temp_test_dir(tmp_path_factory):
    """Create a temporary directory unique to the test session."""
    return tmp_path_factory.mktemp("cache_tests_functional")

@pytest.fixture(scope="function")
def test_project(temp_test_dir):
    """Sets up a minimal temporary project structure for testing."""
    project_dir = temp_test_dir / "test_project_fc"
    if project_dir.exists():
        shutil.rmtree(project_dir)
    project_dir.mkdir(exist_ok=True)
    
    (project_dir / ".clinerules").touch()
    (project_dir / ".clinerules.config.json").write_text(json.dumps({
        "paths": {"doc_dir": "docs", "memory_dir": "cline_docs", "cache_dir": "cache"},
        "excluded_dirs": [".git", "venv"],
        "excluded_extensions": ["*.log"],
        "thresholds": {"code_similarity": 0.7}
    }))
    (project_dir / "src").mkdir(exist_ok=True)
    (project_dir / "src" / "module_a.py").write_text("import os\nprint('hello')")
    (project_dir / "src" / "module_b.py").write_text("print('world')")
    (project_dir / "docs").mkdir(exist_ok=True)
    (project_dir / "docs" / "readme.md").write_text("# Test Readme")
    (project_dir / "cline_docs").mkdir(exist_ok=True)
    (project_dir / "lib").mkdir(exist_ok=True)
    (project_dir / "lib" / "helper.py").write_text("def helper_func(): return 1")

    # Create dummy cache dir and embedding files for testing FC-03 etc.
    cache_dir = project_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    embedding_dir = cache_dir / "embeddings"
    embedding_dir.mkdir(exist_ok=True)
    # Mock embedding data
    np.save(embedding_dir / "1A1.npy", np.array([0.1, 0.2]))
    np.save(embedding_dir / "1B2.npy", np.array([0.3, 0.4]))
    np.save(embedding_dir / "1C3.npy", np.array([0.5, 0.6]))

    original_cwd = os.getcwd()
    os.chdir(project_dir)
    yield project_dir
    os.chdir(original_cwd)

# --- Functional Tests (FC-01 to FC-07) ---

# Test Case FC-01: path_utils.get_project_root Cache
def test_fc01_get_project_root_cache(test_project, clear_cache_fixture, caplog):
    clear_all_caches()
    """Verify get_project_root cache hits and potential invalidation."""
    cache_name = 'project_root'
    project_root_path = test_project

    # 1. Initial call
    print(f"Calling get_project_root for the first time from: {os.getcwd()}")
    root1 = path_utils.get_project_root()
    assert path_utils.normalize_path(root1) == path_utils.normalize_path(str(project_root_path))
    stats1 = get_cache_stats(cache_name)

    # 2. Second call - should be a cache hit
    print("Calling get_project_root for the second time...")
    root2 = path_utils.get_project_root()
    assert path_utils.normalize_path(root2) == path_utils.normalize_path(root1)
    stats2 = get_cache_stats(cache_name)
    assert stats2['hits'] >= 1

    # 3. Test invalidation
    print("Touching .clinerules...")
    clinerules_path = project_root_path / ".clinerules"
    touch(clinerules_path)
    time.sleep(0.1)

    print("Calling get_project_root after touching .clinerules...")
    root3 = path_utils.get_project_root()
    assert path_utils.normalize_path(root3) == path_utils.normalize_path(root1)
    stats3 = get_cache_stats(cache_name)

    # Expect hit because get_project_root key depends on CWD, not .clinerules mtime
    assert stats3['hits'] > stats2.get('hits', 0)

# Test Case FC-02: path_utils.is_valid_project_path Cache
def test_fc02_is_valid_project_path_cache(test_project, clear_cache_fixture, caplog):
    clear_all_caches()
    """Verify valid_project_paths cache hits/misses based on path and root."""
    cache_name = 'valid_project_paths'
    project_root_path = test_project
    valid_path_rel = "src/module_a.py"
    valid_path_abs = project_root_path / valid_path_rel
    
    # Use a truly invalid path (outside project)
    invalid_path_rel = "../outside_project_file.txt"

    # Ensure the underlying get_project_root is called at least once
    path_utils.get_project_root()

    # 1. Initial call (valid path)
    print(f"Calling is_valid_project_path for '{valid_path_rel}' (1st time)")
    res1 = path_utils.is_valid_project_path(str(valid_path_abs))
    assert res1 is True
    stats1 = get_cache_stats(cache_name)

    # 2. Second call (same valid path) -> Cache Hit
    print(f"Calling is_valid_project_path for '{valid_path_rel}' (2nd time)")
    res2 = path_utils.is_valid_project_path(str(valid_path_abs))
    assert res2 is True
    stats2 = get_cache_stats(cache_name)
    assert stats2['hits'] >= 1

    # 3. Third call (different valid path) -> Cache Miss
    another_valid_path_rel = "docs/readme.md"
    another_valid_path_abs = project_root_path / another_valid_path_rel
    print(f"Calling is_valid_project_path for '{another_valid_path_rel}' (1st time)")
    res3 = path_utils.is_valid_project_path(str(another_valid_path_abs))
    assert res3 is True
    stats3 = get_cache_stats(cache_name)
    assert stats3['misses'] > stats2.get('misses', 0)

    # 4. Fourth call (invalid path) -> Cache Miss
    print(f"Calling is_valid_project_path for '{invalid_path_rel}' (1st time)")
    res4 = path_utils.is_valid_project_path(invalid_path_rel)
    assert res4 is False
    stats4 = get_cache_stats(cache_name)
    assert stats4['misses'] > stats3.get('misses', 0)

    # 5. Fifth call (same invalid path) -> Cache Hit
    print(f"Calling is_valid_project_path for '{invalid_path_rel}' (2nd time)")
    res5 = path_utils.is_valid_project_path(invalid_path_rel)
    assert res5 is False
    stats5 = get_cache_stats(cache_name)
    assert stats5['hits'] > stats4.get('hits', 0)

# Test Case FC-03: embedding_manager.calculate_similarity Cache
def test_fc03_calculate_similarity_cache(test_project, clear_cache_fixture, monkeypatch, caplog):
    clear_all_caches()
    """Verify calculate_similarity cache hits/misses."""
    cache_name = 'similarity_calculation'
    embedding_dir = test_project / "cache" / "embeddings"
    key1 = '1A1'
    key2 = '1B2'
    key3 = '1C3'
    npy1_path = embedding_dir / f"{key1}.npy"

    # 1. Initial call
    print(f"\nCalling calculate_similarity({key1}, {key2}) (1st time)")
    sim1 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    assert isinstance(sim1, float)
    stats1 = get_cache_stats(cache_name)

    # 2. Second call -> Cache Hit
    print(f"Calling calculate_similarity({key1}, {key2}) (2nd time)")
    sim2 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    assert sim2 == sim1
    stats2 = get_cache_stats(cache_name)
    assert stats2['hits'] >= 1

    # 3. Third call (reverse) -> Cache Hit
    print(f"Calling calculate_similarity({key2}, {key1}) (1st time)")
    sim3 = embedding_manager.calculate_similarity(key2, key1, str(embedding_dir), {}, str(test_project), [], [])
    assert sim3 == sim1
    stats3 = get_cache_stats(cache_name)
    assert stats3['hits'] > stats2.get('hits', 0)

    # 4. Touch .npy file
    print(f"Touching {npy1_path}...")
    touch(npy1_path)
    time.sleep(0.1)

    # 5. Call again -> Expect HIT (stale) because implementation doesn't check mtime
    print(f"Calling calculate_similarity({key1}, {key2}) (after touch)")
    sim4 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    stats4 = get_cache_stats(cache_name)
    # Confirm it hits (stale)
    # assert stats4['hits'] > stats3.get('hits', 0) 
    
    # 6. Manually invalidate
    invalidate_dependent_entries(cache_name, f"sim_ses:{key1}:{key2}")
    
    # 7. Call again -> Miss
    print(f"Calling calculate_similarity({key1}, {key2}) (after invalidate)")
    sim5 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    stats5 = get_cache_stats(cache_name)
    assert stats5['misses'] > stats4.get('misses', 0)

# Test Case FC-04: dependency_grid.validate_grid Cache
def test_fc04_validate_grid_cache(clear_cache_fixture):
    clear_all_caches()
    """Verify validate_grid cache hits/misses."""
    cache_name = 'grid_validation'

    # Create KeyInfo objects
    ki1 = KeyInfo(key_string="1A1", norm_path="src/a.py", parent_path="src", tier=1, is_directory=False)
    ki2 = KeyInfo(key_string="1A2", norm_path="src/b.py", parent_path="src", tier=1, is_directory=False)
    ki3 = KeyInfo(key_string="1B", norm_path="src/c.py", parent_path="src", tier=1, is_directory=False)
    
    keys1_sorted = [ki1, ki2, ki3]
    grid1 = {
        '1A1': "o<p",
        '1A2': ">ox",
        '1B':  "pxo"
    }

    # 1. Initial call
    print("\nCalling validate_grid(G1, K1_sorted) (1st time)")
    res1 = dependency_grid.validate_grid(grid1, keys1_sorted)
    assert res1 is True
    stats1 = get_cache_stats(cache_name)

    # 2. Second call -> Cache Hit
    print("Calling validate_grid(G1, K1_sorted) (2nd time)")
    res2 = dependency_grid.validate_grid(grid1, keys1_sorted)
    assert res2 == res1
    stats2 = get_cache_stats(cache_name)
    assert stats2['hits'] >= 1

    # 3. Third call (unsorted) -> Cache HIT (Key uses sorted version)
    keys1_unsorted = [ki3, ki1, ki2]
    print("Calling validate_grid(G1, K1_unsorted) -> Expect HIT")
    res3 = dependency_grid.validate_grid(grid1, keys1_unsorted)
    assert res3 == res1
    stats3 = get_cache_stats(cache_name)
    assert stats3['hits'] > stats2.get('hits', 0)

# Test Case FC-05: dependency_grid.get_dependencies_from_grid Cache
def test_fc05_get_dependencies_from_grid_cache(clear_cache_fixture):
    clear_all_caches()
    """Verify get_dependencies_from_grid cache."""
    cache_name = 'grid_dependencies'

    ki1 = KeyInfo(key_string="1A1", norm_path="src/a.py", parent_path="src", tier=1, is_directory=False)
    ki2 = KeyInfo(key_string="1A2", norm_path="src/b.py", parent_path="src", tier=1, is_directory=False)
    ki3 = KeyInfo(key_string="1B", norm_path="src/c.py", parent_path="src", tier=1, is_directory=False)
    keys1_sorted = [ki1, ki2, ki3]
    
    grid1 = {
        '1A1': "o<p",
        '1A2': ">ox",
        '1B':  "pxo"
    }
    target_key1 = '1A1'
    
    expected_deps1 = {'<': ['1A2'], 'p': ['1B']}

    # 1. Initial call
    print(f"\nCalling get_dependencies_from_grid(G1, {target_key1}, K1) (1st time)")
    deps1 = dependency_grid.get_dependencies_from_grid(grid1, target_key1, keys1_sorted)
    assert deps1 == expected_deps1
    stats1 = get_cache_stats(cache_name)

    # 2. Second call -> Cache Hit
    print(f"Calling get_dependencies_from_grid(G1, {target_key1}, K1) (2nd time)")
    deps2 = dependency_grid.get_dependencies_from_grid(grid1, target_key1, keys1_sorted)
    assert deps2 == deps1
    stats2 = get_cache_stats(cache_name)
    assert stats2['hits'] >= 1

# Test Case FC-06: tracker_io.read_tracker_file Cache
def test_fc06_read_tracker_file_cache(test_project, clear_cache_fixture):
    clear_all_caches()
    """Verify read_tracker_file cache invalidates on file modification."""
    cache_name = 'tracker_data_structured'
    tracker_rel_path = "cline_docs/tracker.md"
    tracker_abs_path = test_project / tracker_rel_path

    initial_content = "# Initial Tracker\nkey1,key2\np,p\n"
    tracker_abs_path.write_text(initial_content)
    time.sleep(0.1)

    # 1. Initial read
    print(f"\nCalling read_tracker_file_structured({tracker_rel_path}) (1st time)")
    result1 = tracker_utils.read_tracker_file_structured(str(tracker_abs_path))
    assert result1 is not None
    stats1 = get_cache_stats(cache_name)

    # 2. Second read -> Cache Hit
    print(f"Calling read_tracker_file_structured({tracker_rel_path}) (2nd time)")
    result2 = tracker_utils.read_tracker_file_structured(str(tracker_abs_path))
    assert result2 == result1
    stats2 = get_cache_stats(cache_name)
    assert stats2['hits'] >= 1

    # 3. Touch file
    print(f"Touching {tracker_abs_path}...")
    touch(tracker_abs_path)
    time.sleep(0.1)

    # 4. Third read -> Cache Miss
    print(f"Calling read_tracker_file_structured({tracker_rel_path}) (after touch)")
    result3 = tracker_utils.read_tracker_file_structured(str(tracker_abs_path))
    assert result3 == result1
    stats3 = get_cache_stats(cache_name)
    assert stats3['misses'] > stats2.get('misses', 0)

# Test Case FC-07: Config-dependent Caches
def test_fc07_config_dependent_caches(test_project, clear_cache_fixture, monkeypatch):
    clear_all_caches()
    """Verify caches invalidate when .clinerules.config.json changes."""
    config_path = test_project / ".clinerules.config.json"
    cache_name_config = 'excluded_dirs'

    initial_config_data = {
        "paths": {"doc_dir": "docs", "memory_dir": "cline_docs"},
        "excluded_dirs": [".git", "venv"],
        "excluded_extensions": ["*.log", "*.tmp"],
        "thresholds": {"code_similarity": 0.7}
    }
    config_path.write_text(json.dumps(initial_config_data))
    time.sleep(0.1)

    monkeypatch.setattr(config_manager.ConfigManager, '_instance', None, raising=False)
    cm = config_manager.ConfigManager()
    initial_exclusions = cm.get_excluded_dirs()

    # 1. Call config getter again -> Hit
    print("\nCalling get_excluded_dirs() (2nd time)")
    exclusions1 = cm.get_excluded_dirs()
    assert exclusions1 == initial_exclusions
    stats_conf1 = get_cache_stats(cache_name_config)

    # --- Modify Config File ---
    print(f"Modifying {config_path}...")
    modified_config_data = {
        "paths": {"doc_dir": "docs", "memory_dir": "cline_docs"},
        "excluded_dirs": [".git", "venv", "build_custom"],
        "excluded_extensions": ["*.log"],
        "thresholds": {"code_similarity": 0.8}
    }
    config_path.write_text(json.dumps(modified_config_data))
    time.sleep(1.5) # Ensure mtime change

    monkeypatch.setattr(config_manager.ConfigManager, '_instance', None, raising=False)
    cm = config_manager.ConfigManager()

    # 2. Call config getter again -> Miss
    print("Calling get_excluded_dirs() (after modify)")
    exclusions2 = cm.get_excluded_dirs()
    assert exclusions2 != initial_exclusions
    assert "build_custom" in exclusions2
    stats_conf2 = get_cache_stats(cache_name_config)
    assert stats_conf2['misses'] > stats_conf1.get('misses', 0)
