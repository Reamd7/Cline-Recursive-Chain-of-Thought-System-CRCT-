# runtime_inspector.py
import inspect
import sys
import os
import json
import importlib.util
import logging
import typing
import ast
import textwrap
from typing import Dict, Any, List, Set, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_type_annotations(obj) -> Dict[str, Any]:
    """Extract parameter and return type annotations."""
    try:
        return {
            'parameters': {k: str(v) for k, v in typing.get_type_hints(obj, include_extras=True).items()},
            'return_type': str(inspect.signature(obj).return_annotation)
        }
    except Exception:
        return {}

def get_source_context(obj, code_roots: List[str]) -> Dict[str, Any]:
    """
    Get source file location and import context.
    Returns empty dict if source is outside code roots.
    """
    try:
        source_file = inspect.getsourcefile(obj)
        if not source_file:
            return {}
        
        # Normalize and validate against code roots
        from cline_utils.dependency_system.utils.path_utils import normalize_path, is_subpath
        norm_source = normalize_path(source_file)
        
        # Check if file is within any code root
        in_code_roots = False
        for code_root in code_roots:
            norm_root = normalize_path(code_root)
            if norm_source == norm_root or is_subpath(norm_source, norm_root):
                in_code_roots = True
                break
        
        if not in_code_roots:
            logger.debug(f"Skipping source outside code roots: {norm_source}")
            return {}
        
        source_lines, start_line = inspect.getsourcelines(obj)
        # Strip line endings to prevent escape artifacts in JSON (improves embedding quality)
        clean_source_lines = [line.rstrip('\n').rstrip('\r') for line in source_lines]
        return {
            'file': norm_source,
            'line_range': (start_line, start_line + len(source_lines)),
            'source_lines': clean_source_lines
        }
    except Exception:
        return {}

def get_module_exports(module) -> Dict[str, str]:
    """Identify all exported symbols and their origins."""
    exports = {}
    if hasattr(module, '__all__'):
        for name in module.__all__:
            obj = getattr(module, name, None)
            if obj:
                try:
                    exports[name] = inspect.getmodule(obj).__name__
                except AttributeError:
                    pass
    return exports

def get_inheritance_info(cls, code_roots: List[str]) -> Dict[str, Any]:
    """
    Extract inheritance hierarchy and method resolution order.
    Only includes bases/mro that are within code roots.
    """
    from cline_utils.dependency_system.utils.path_utils import normalize_path, is_subpath
    
    try:
        bases = []
        for base in cls.__bases__:
            try:
                base_file = inspect.getsourcefile(base)
                if base_file:
                    norm_base_file = normalize_path(base_file)
                    # Check if base is in code roots
                    in_roots = any(
                        norm_base_file == normalize_path(root) or 
                        is_subpath(norm_base_file, normalize_path(root))
                        for root in code_roots
                    )
                    if in_roots:
                        bases.append(base.__module__ + '.' + base.__qualname__)
            except (TypeError, AttributeError):
                pass
        
        mro = []
        for c in inspect.getmro(cls)[1:]:  # Skip self
            try:
                c_file = inspect.getsourcefile(c)
                if c_file:
                    norm_c_file = normalize_path(c_file)
                    in_roots = any(
                        norm_c_file == normalize_path(root) or 
                        is_subpath(norm_c_file, normalize_path(root))
                        for root in code_roots
                    )
                    if in_roots:
                        mro.append(c.__module__ + '.' + c.__qualname__)
            except (TypeError, AttributeError):
                pass
        
        return {
            'bases': bases,
            'mro': mro
        }
    except Exception:
        return {}

def get_closure_dependencies(func, code_roots: List[str]) -> List[str]:
    """
    Identify variables captured in function closures.
    Only includes modules within code roots.
    """
    from cline_utils.dependency_system.utils.path_utils import normalize_path, is_subpath
    
    deps = []
    if inspect.isfunction(func) and func.__closure__:
        for cell in func.__closure__:
            try:
                obj = cell.cell_contents
                module = inspect.getmodule(obj)
                if module:
                    try:
                        module_file = inspect.getsourcefile(module)
                        if module_file:
                            norm_module_file = normalize_path(module_file)
                            in_roots = any(
                                norm_module_file == normalize_path(root) or 
                                is_subpath(norm_module_file, normalize_path(root))
                                for root in code_roots
                            )
                            if in_roots:
                                deps.append(module.__name__)
                    except (TypeError, AttributeError):
                        pass
            except Exception:
                pass
    return list(set(deps))

def get_decorator_info(obj, code_roots: List[str]) -> List[str]:
    """
    Extract decorator information from wrapped objects.
    Only includes decorators from modules within code roots.
    """
    from cline_utils.dependency_system.utils.path_utils import normalize_path, is_subpath
    
    decorators = []
    while hasattr(obj, '__wrapped__'):
        try:
            wrapper_module = inspect.getmodule(obj)
            if wrapper_module:
                try:
                    wrapper_file = inspect.getsourcefile(wrapper_module)
                    if wrapper_file:
                        norm_wrapper_file = normalize_path(wrapper_file)
                        in_roots = any(
                            norm_wrapper_file == normalize_path(root) or 
                            is_subpath(norm_wrapper_file, normalize_path(root))
                            for root in code_roots
                        )
                        if in_roots:
                            decorators.append(wrapper_module.__name__)
                except (TypeError, AttributeError):
                    pass
            obj = obj.__wrapped__
        except Exception:
            break
    return decorators

def get_scope_references(func) -> Dict[str, List[str]]:
    """Extract global and nonlocal variable references."""
    try:
        code = func.__code__
        return {
            'globals': list(code.co_names),
            'nonlocals': list(code.co_freevars)
        }
    except Exception:
        return {}

def get_attribute_accesses(source_code: str) -> Set[str]:
    """Parse source to identify attribute access patterns."""
    accesses = set()
    try:
        dedented_source = textwrap.dedent(source_code)
        tree = ast.parse(dedented_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                accesses.add(node.attr)
    except Exception:
        pass
    return list(accesses)

def get_module_info(file_path: str, module_name: str, code_roots: List[str]) -> Dict[str, Any]:
    """
    Safely imports a module and extracts symbol information using inspect.
    All collected paths are validated against code_roots.
    """
    try:
        # Add file directory to sys.path to handle relative imports if needed
        file_dir = os.path.dirname(file_path)
        if file_dir not in sys.path:
            sys.path.insert(0, file_dir)

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return {}

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        symbols = {
            "classes": [],
            "functions": [],
            "exports": get_module_exports(module)
        }

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module_name:
                source_context = get_source_context(obj, code_roots)
                
                # Skip if source is outside code roots
                if not source_context:
                    logger.debug(f"Skipping class {name} - source outside code roots")
                    continue
                
                class_info = {
                    "name": name,
                    "docstring": inspect.getdoc(obj),
                    "inheritance": get_inheritance_info(obj, code_roots),
                    "decorators": get_decorator_info(obj, code_roots),
                    "source_context": source_context,
                    "methods": []
                }

                for method_name, method in inspect.getmembers(obj):
                    if inspect.isfunction(method) or inspect.ismethod(method):
                        # Validate method source
                        method_source_context = get_source_context(method, code_roots)
                        if not method_source_context:
                            logger.debug(f"Skipping method {method_name} - source outside code roots")
                            continue
                        
                        try:
                            sig = str(inspect.signature(method))
                        except ValueError:
                            sig = "(...)"

                        # Get source code for attribute access analysis
                        try:
                            source = inspect.getsource(method)
                            attr_accesses = get_attribute_accesses(source)
                        except Exception:
                            attr_accesses = []

                        class_info["methods"].append({
                            "name": method_name,
                            "signature": sig,
                            "docstring": inspect.getdoc(method),
                            "type_annotations": get_type_annotations(method),
                            "closure_dependencies": get_closure_dependencies(method, code_roots),
                            "scope_references": get_scope_references(method),
                            "decorators": get_decorator_info(method, code_roots),
                            "source_context": method_source_context,
                            "attribute_accesses": attr_accesses
                        })

                symbols["classes"].append(class_info)

            elif inspect.isfunction(obj) and obj.__module__ == module_name:
                source_context = get_source_context(obj, code_roots)
                
                # Skip if source is outside code roots
                if not source_context:
                    logger.debug(f"Skipping function {name} - source outside code roots")
                    continue
                
                try:
                    sig = str(inspect.signature(obj))
                except ValueError:
                    sig = "(...)"

                # Get source code for attribute access analysis
                try:
                    source = inspect.getsource(obj)
                    attr_accesses = get_attribute_accesses(source)
                except Exception:
                    attr_accesses = []

                symbols["functions"].append({
                    "name": name,
                    "signature": sig,
                    "docstring": inspect.getdoc(obj),
                    "type_annotations": get_type_annotations(obj),
                    "closure_dependencies": get_closure_dependencies(obj, code_roots),
                    "scope_references": get_scope_references(obj),
                    "decorators": get_decorator_info(obj, code_roots),
                    "source_context": source_context,
                    "attribute_accesses": attr_accesses
                })

        return symbols

    except Exception as e:
        logger.warning(f"Failed to inspect {file_path}: {e}")
        return {}
    finally:
        # Cleanup sys.path
        if file_dir in sys.path:
            sys.path.remove(file_dir)

def main():
    if len(sys.argv) < 2:
        print("Usage: python runtime_inspector.py <project_root>")
        sys.exit(1)

    project_root = os.path.abspath(sys.argv[1])

    # Add project root to sys.path to allow importing cline_utils
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from cline_utils.dependency_system.utils.config_manager import ConfigManager
        from cline_utils.dependency_system.utils.path_utils import normalize_path
    except ImportError as e:
        logger.error(f"Could not import ConfigManager: {e}. Ensure cline_utils is in python path.")
        sys.exit(1)

    # Initialize ConfigManager
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        config_manager = ConfigManager()
        
        # Get configuration - code_roots are already normalized by config_manager
        code_roots = config_manager.get_code_root_directories()
        excluded_dirs = set(config_manager.get_excluded_dirs())
        excluded_extensions = set(config_manager.get_excluded_extensions())
        excluded_paths = set(config_manager.get_excluded_paths())

        logger.info(f"Loaded configuration. Code roots: {code_roots}")

        # Convert relative code roots to absolute paths
        absolute_code_roots = []
        for root_dir_rel in code_roots:
            if os.path.isabs(root_dir_rel):
                absolute_code_roots.append(normalize_path(root_dir_rel))
            else:
                absolute_code_roots.append(normalize_path(os.path.join(project_root, root_dir_rel)))

        logger.info(f"Absolute code roots for validation: {absolute_code_roots}")

        # Save to cline_utils/dependency_system/core/runtime_symbols.json
        core_dir = os.path.join(project_root, "cline_utils", "dependency_system", "core")
        os.makedirs(core_dir, exist_ok=True)
        output_file = os.path.join(core_dir, "runtime_symbols.json")

        all_symbols = {}

        if not code_roots:
            logger.warning("No code roots defined in configuration. Skipping runtime inspection.")
            sys.exit(0)

        # Process each root
        for root_dir_rel in code_roots:
            # Resolve to absolute path
            if os.path.isabs(root_dir_rel):
                root_dir = root_dir_rel
            else:
                root_dir = os.path.join(project_root, root_dir_rel)
            
            root_dir = normalize_path(root_dir)

            if not os.path.exists(root_dir):
                logger.warning(f"Code root not found: {root_dir}")
                continue

            logger.info(f"Scanning root: {root_dir}")

            for root, dirs, files in os.walk(root_dir):
                root = normalize_path(root)

                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if d not in excluded_dirs]

                # Filter by path (excluded_paths)
                valid_dirs = []
                for d in dirs:
                    dir_path = normalize_path(os.path.join(root, d))
                    if dir_path not in excluded_paths:
                        valid_dirs.append(d)
                dirs[:] = valid_dirs

                for file in files:
                    if not file.endswith(".py") or file.startswith("__"):
                        continue

                    _, ext = os.path.splitext(file)
                    if ext in excluded_extensions:
                        continue

                    file_path = normalize_path(os.path.join(root, file))
                    if file_path in excluded_paths:
                        continue

                    # Construct a module name (approximate)
                    rel_path = os.path.relpath(file_path, project_root)
                    module_name = rel_path.replace(os.sep, ".").replace(".py", "")

                    logger.info(f"Inspecting {module_name}...")
                    
                    # Pass absolute_code_roots to get_module_info for validation
                    info = get_module_info(file_path, module_name, absolute_code_roots)
                    if info:
                        all_symbols[file_path] = info

        # Use ensure_ascii=False to prevent escape character pollution in embeddings
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_symbols, f, indent=2, ensure_ascii=False)

        logger.info(f"Runtime inspection complete. Saved to {output_file}")

    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
