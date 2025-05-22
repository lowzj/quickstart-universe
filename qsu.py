import argparse
import pathlib
import subprocess


def main():
    parser = argparse.ArgumentParser(description="Starts a component.")
    parser.add_argument("component_name", help="Name of the component to start.")
    args = parser.parse_args()

    component_name = args.component_name
    script_dir = pathlib.Path(__file__).parent.resolve()  # Renamed current_dir
    comp_home = script_dir / component_name

    start_script_path = comp_home / "start.sh"  # Full path to the script

    if comp_home.is_dir() and start_script_path.is_file():
        print(f"starting {component_name} ...")
        try:
            # Execute start.sh using its name, with cwd set to its directory
            subprocess.run(["./start.sh"], check=True, cwd=comp_home)
            print(f"Component {component_name} started successfully.")
        except FileNotFoundError:
            # This error means that the command "./start.sh" was not found by subprocess.run
            # when executed with cwd=comp_home.
            print(
                f"Error: The script {start_script_path} was not found or could not be executed in {comp_home}."
            )
        except subprocess.CalledProcessError as e:
            print(f"Error starting component {component_name}: {e}")
        except Exception as e:  # Generic catch-all
            print(f"An unexpected error occurred: {e}")
    else:
        print(f"no component {component_name}")


if __name__ == "__main__":
    main()
