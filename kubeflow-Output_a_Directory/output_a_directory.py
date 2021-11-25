import kfp
from kfp.components import create_component_from_func, load_component_from_text, InputPath, OutputPath

EXPERIMENT_NAME = 'Output a directory' # Name of the experiment in the UI
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

# Outputting directories from Python-based components:
@create_component_from_func
def produce_dir_with_files_python_op(output_dir_path: OutputPath(), num_files: int = 10):
	import os
	os.makedirs(output_dir_path, exist_ok=True)
	for i in range(num_files):
		file_path = os.path.join(output_dir_path, str(i) + '.txt')
		with open(file_path, 'w') as f:
			f.write(str(i))

@create_component_from_func
def list_dir_files_python_op(input_dir_path: InputPath()):
	import os
	dir_items = os.listdir(input_dir_path)
	for dir_item in dir_items:
		print(dir_item)

produce_dir_with_files_general_op = load_component_from_text('''
name: Produce directory
inputs:
- {name: num_files, type: Integer}
outputs:
- {name: output_dir}
implementation:
	container:
		image: alpine
		command:
		- sh
		- -ecx
		- |
			num_files="$0"
			output_path="$1"
			mkdir -p "$output_path"
			for i in $(seq "$num_files"); do
				echo "$i" > "$output_path/${i}.txt"
			done
		- {inputValue: num_files}
		- {outputPath: output_dir}
''')

list_dir_files_general_op = load_component_from_text('''
name: List dir files
inputs:
- {name: input_dir}
implementation:
	container:
		image: alpine
		command:
		- ls
		- {inputPath: input_dir}
''')

# Test pipeline
def dir_pipeline():
	produce_dir_python_task = produce_dir_with_files_python_op(num_files=15)
	list_dir_files_python_op(input_dir=produce_dir_python_task.output)

	produce_dir_general_task = produce_dir_with_files_general_op(num_files=15)
	list_dir_files_general_op(input_dir=produce_dir_general_task.output)

if __name__ == '__main__':
	kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
		dir_pipeline,
		arguments={},
		experiment_name=EXPERIMENT_NAME)