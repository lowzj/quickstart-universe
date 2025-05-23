import unittest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import io
import os

# Add the project root to the Python path to allow importing qsu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import qsu  # The module to be tested


class TestQsu(unittest.TestCase):
    def setUp(self):
        # Define a consistent base path string for mocks to use
        self.mock_app_dir_str = "/app"

        # Mock object for script_dir (e.g., /app) - qsu.py's directory
        self.mock_script_dir_obj = MagicMock(name="mock_script_dir_obj")
        self.mock_script_dir_obj.__fspath__ = MagicMock(
            return_value=self.mock_app_dir_str
        )
        self.mock_script_dir_obj.__str__ = MagicMock(return_value=self.mock_app_dir_str)

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("qsu.subprocess.run")
    @patch("qsu.pathlib.Path")  # Patches the Path class in qsu's namespace
    @patch("qsu.argparse.ArgumentParser")  # Patching ArgumentParser constructor
    def test_successful_component_start(
        self,
        mock_ArgumentParser_constructor,
        mock_Path_class_in_qsu,
        mock_subprocess_run,
        mock_stdout,
    ):
        component_name = "kafka"

        # Setup argparse mock
        mock_args = MagicMock()
        mock_args.component_name = component_name
        mock_parser_instance = mock_ArgumentParser_constructor.return_value
        mock_parser_instance.parse_args.return_value = mock_args

        # --- Configure pathlib.Path related mocks ---
        # 1. For `script_dir = pathlib.Path(__file__).parent.resolve()`
        mock_file_path_obj = MagicMock(name="mock_file_path_obj")  # No spec
        # When Path(qsu.__file__) is called, it returns this mock_file_path_obj
        mock_Path_class_in_qsu.return_value = mock_file_path_obj

        mock_script_parent_obj = MagicMock(name="mock_script_parent_obj")  # No spec
        mock_file_path_obj.parent = mock_script_parent_obj
        mock_script_parent_obj.resolve = MagicMock(
            return_value=self.mock_script_dir_obj
        )

        # 2. For `comp_home = script_dir / component_name`
        mock_comp_home_obj = MagicMock(name="mock_comp_home_obj")  # No spec
        comp_home_path_str = os.path.join(self.mock_app_dir_str, component_name)
        mock_comp_home_obj.__fspath__ = MagicMock(
            return_value=comp_home_path_str
        )  # For cwd argument
        mock_comp_home_obj.__str__ = MagicMock(
            return_value=comp_home_path_str
        )  # For string interpolation
        self.mock_script_dir_obj.__truediv__ = MagicMock(
            return_value=mock_comp_home_obj
        )

        # 3. For `start_script_path = comp_home / "start.sh"`
        mock_start_script_obj = MagicMock(name="mock_start_script_obj")  # No spec
        start_script_full_path_str = os.path.join(comp_home_path_str, "start.sh")
        mock_start_script_obj.__fspath__ = MagicMock(
            return_value=start_script_full_path_str
        )
        mock_start_script_obj.__str__ = MagicMock(
            return_value=start_script_full_path_str
        )  # Consistent str
        mock_comp_home_obj.__truediv__ = MagicMock(return_value=mock_start_script_obj)

        # Conditions for if block
        mock_comp_home_obj.is_dir.return_value = True
        mock_start_script_obj.is_file.return_value = True

        # Configure subprocess.run mock
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["./start.sh"], returncode=0
        )

        qsu.main()

        output_lines = mock_stdout.getvalue().splitlines()

        self.assertIn(f"starting {component_name} ...", output_lines)
        self.assertIn(f"Component {component_name} started successfully.", output_lines)

        mock_Path_class_in_qsu.assert_called_once_with(qsu.__file__)
        self.mock_script_dir_obj.__truediv__.assert_called_once_with(component_name)
        mock_comp_home_obj.__truediv__.assert_called_once_with("start.sh")

        mock_subprocess_run.assert_called_once_with(
            ["./start.sh"], check=True, cwd=mock_comp_home_obj
        )

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("qsu.subprocess.run")
    @patch("qsu.pathlib.Path")
    @patch("qsu.argparse.ArgumentParser")
    def test_non_existent_component_directory(
        self,
        mock_ArgumentParser_constructor,
        mock_Path_class_in_qsu,
        mock_subprocess_run,
        mock_stdout,
    ):
        component_name = "phantom_component"
        mock_args = MagicMock()
        mock_args.component_name = component_name
        mock_parser_instance = mock_ArgumentParser_constructor.return_value
        mock_parser_instance.parse_args.return_value = mock_args

        mock_file_path_obj = MagicMock(name="mock_file_path_obj")
        mock_Path_class_in_qsu.return_value = mock_file_path_obj
        mock_script_parent_obj = MagicMock(name="mock_script_parent_obj")
        mock_file_path_obj.parent = mock_script_parent_obj
        mock_script_parent_obj.resolve = MagicMock(
            return_value=self.mock_script_dir_obj
        )

        mock_comp_home_obj = MagicMock(name="mock_comp_home_obj")
        self.mock_script_dir_obj.__truediv__ = MagicMock(
            return_value=mock_comp_home_obj
        )

        mock_start_script_obj = MagicMock(name="mock_start_script_obj")
        mock_comp_home_obj.__truediv__ = MagicMock(
            return_value=mock_start_script_obj
        )  # For start_script_path

        mock_comp_home_obj.is_dir.return_value = False  # Key for this test scenario

        qsu.main()

        self.assertEqual(
            f"no component {component_name}", mock_stdout.getvalue().strip()
        )
        mock_subprocess_run.assert_not_called()

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("qsu.subprocess.run")
    @patch("qsu.pathlib.Path")
    @patch("qsu.argparse.ArgumentParser")
    def test_start_sh_missing(
        self,
        mock_ArgumentParser_constructor,
        mock_Path_class_in_qsu,
        mock_subprocess_run,
        mock_stdout,
    ):
        component_name = "scriptless_component"
        mock_args = MagicMock()
        mock_args.component_name = component_name
        mock_parser_instance = mock_ArgumentParser_constructor.return_value
        mock_parser_instance.parse_args.return_value = mock_args

        mock_file_path_obj = MagicMock(name="mock_file_path_obj")
        mock_Path_class_in_qsu.return_value = mock_file_path_obj
        mock_script_parent_obj = MagicMock(name="mock_script_parent_obj")
        mock_file_path_obj.parent = mock_script_parent_obj
        mock_script_parent_obj.resolve = MagicMock(
            return_value=self.mock_script_dir_obj
        )

        mock_comp_home_obj = MagicMock(name="mock_comp_home_obj")
        self.mock_script_dir_obj.__truediv__ = MagicMock(
            return_value=mock_comp_home_obj
        )

        mock_start_script_obj = MagicMock(name="mock_start_script_obj")
        mock_comp_home_obj.__truediv__ = MagicMock(return_value=mock_start_script_obj)

        mock_comp_home_obj.is_dir.return_value = True
        mock_start_script_obj.is_file.return_value = False  # Key for this test

        qsu.main()

        self.assertEqual(
            f"no component {component_name}", mock_stdout.getvalue().strip()
        )
        mock_subprocess_run.assert_not_called()

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("qsu.subprocess.run")
    @patch("qsu.pathlib.Path")
    @patch("qsu.argparse.ArgumentParser")
    def test_execution_fails_called_process_error(
        self,
        mock_ArgumentParser_constructor,
        mock_Path_class_in_qsu,
        mock_subprocess_run,
        mock_stdout,
    ):
        component_name = "failing_component"
        mock_args = MagicMock()
        mock_args.component_name = component_name
        mock_parser_instance = mock_ArgumentParser_constructor.return_value
        mock_parser_instance.parse_args.return_value = mock_args

        mock_file_path_obj = MagicMock(name="mock_file_path_obj")
        mock_Path_class_in_qsu.return_value = mock_file_path_obj
        mock_script_parent_obj = MagicMock(name="mock_script_parent_obj")
        mock_file_path_obj.parent = mock_script_parent_obj
        mock_script_parent_obj.resolve = MagicMock(
            return_value=self.mock_script_dir_obj
        )

        mock_comp_home_obj = MagicMock(name="mock_comp_home_obj")
        comp_home_path_str = os.path.join(self.mock_app_dir_str, component_name)
        mock_comp_home_obj.__fspath__ = MagicMock(return_value=comp_home_path_str)
        mock_comp_home_obj.__str__ = MagicMock(return_value=comp_home_path_str)
        self.mock_script_dir_obj.__truediv__ = MagicMock(
            return_value=mock_comp_home_obj
        )

        mock_start_script_obj = MagicMock(name="mock_start_script_obj")
        mock_comp_home_obj.__truediv__ = MagicMock(return_value=mock_start_script_obj)

        mock_comp_home_obj.is_dir.return_value = True
        mock_start_script_obj.is_file.return_value = True

        error_obj = subprocess.CalledProcessError(returncode=1, cmd=["./start.sh"])
        mock_subprocess_run.side_effect = error_obj

        qsu.main()

        output_lines = mock_stdout.getvalue().splitlines()
        expected_error_message = (
            f"Error starting component {component_name}: {error_obj}"
        )

        self.assertIn(f"starting {component_name} ...", output_lines)
        self.assertIn(expected_error_message, output_lines)
        mock_subprocess_run.assert_called_once_with(
            ["./start.sh"], check=True, cwd=mock_comp_home_obj
        )

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("qsu.subprocess.run")
    @patch("qsu.pathlib.Path")
    @patch("qsu.argparse.ArgumentParser")
    def test_start_sh_not_found_by_subprocess(
        self,
        mock_ArgumentParser_constructor,
        mock_Path_class_in_qsu,
        mock_subprocess_run,
        mock_stdout,
    ):
        component_name = "subprocess_fnf_component"
        mock_args = MagicMock()
        mock_args.component_name = component_name
        mock_parser_instance = mock_ArgumentParser_constructor.return_value
        mock_parser_instance.parse_args.return_value = mock_args

        mock_file_path_obj = MagicMock(name="mock_file_path_obj")
        mock_Path_class_in_qsu.return_value = mock_file_path_obj
        mock_script_parent_obj = MagicMock(name="mock_script_parent_obj")
        mock_file_path_obj.parent = mock_script_parent_obj
        mock_script_parent_obj.resolve = MagicMock(
            return_value=self.mock_script_dir_obj
        )

        mock_comp_home_obj = MagicMock(name="mock_comp_home_obj")
        comp_home_path_str = os.path.join(self.mock_app_dir_str, component_name)
        mock_comp_home_obj.__fspath__ = MagicMock(return_value=comp_home_path_str)
        mock_comp_home_obj.__str__ = MagicMock(
            return_value=comp_home_path_str
        )  # For the {comp_home} part of the message
        self.mock_script_dir_obj.__truediv__ = MagicMock(
            return_value=mock_comp_home_obj
        )

        mock_start_script_obj = MagicMock(name="mock_start_script_obj")
        # FIX: Explicitly mock __str__ for mock_start_script_obj
        # This ensures that when qsu.py formats `start_script_path` in the FNF error message,
        # it uses this defined string value. The prompt indicates qsu.py uses:
        # print(f"Error: The script {start_script_path} was not found or could not be executed in {comp_home}.")
        mock_start_script_obj.__str__ = MagicMock(
            return_value="./start.sh"
        )  # <--- THE FIX
        mock_comp_home_obj.__truediv__ = MagicMock(return_value=mock_start_script_obj)

        mock_comp_home_obj.is_dir.return_value = True
        mock_start_script_obj.is_file.return_value = (
            True  # Script file exists by initial check
        )

        mock_subprocess_run.side_effect = FileNotFoundError(
            "script not found by subprocess.run mock"
        )

        qsu.main()

        output_lines = mock_stdout.getvalue().splitlines()

        # Construct the expected error message based on qsu.py's f-string and mocked __str__ values
        # qsu.py is assumed to print: print(f"Error: The script {start_script_path} was not found or could not be executed in {comp_home}.")
        expected_script_name_in_msg = (
            "./start.sh"  # This is what str(mock_start_script_obj) will return
        )
        expected_error_message = f"Error: The script {expected_script_name_in_msg} was not found or could not be executed in {comp_home_path_str}."

        self.assertIn(f"starting {component_name} ...", output_lines)
        self.assertIn(
            expected_error_message,
            output_lines,
            f"Expected error message not found. Full output: {output_lines}",
        )
        mock_subprocess_run.assert_called_once_with(
            ["./start.sh"], check=True, cwd=mock_comp_home_obj
        )


if __name__ == "__main__":
    unittest.main()
