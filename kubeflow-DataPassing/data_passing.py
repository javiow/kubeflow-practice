import kfp
from kfp.components import func_to_container_op, InputPath, OutputPath

EXPERIMENT_NAME = 'Data Passing'
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

@func_to_container_op
# OutputPath -> 해당 컴포넌트의 출력값이 그 다음 컴포넌트의 입력값으로 연결됨
def repeat_line(line: str, output_text_path: OutputPath(str), count: int = 10):
	'''Repeat the line specified number of times'''
	with open(output_text_path, 'w') as writer:
		for i in range(count):
			writer.write(line + '\n')

@func_to_container_op
# 컴포넌트에서 컴포넌트로 파일을 전달할 때 MinIO의 오브젝트 스토리지를 사용
def print_text(text_path: InputPath()): # The "text" input is untyped so that any data can be printed
	'''Print text'''
	with open(text_path, 'r') as reader:
		for line in reader:
			print(line, end = '')

def print_repeating_lines_pipeline():
	repeat_lines_task = repeat_line(line='Hello', count=5000)
	print_text(repeat_lines_task.output) # Don't forget .output !

@func_to_container_op
def split_text_lines(source_path: InputPath(str), odd_lines_path: OutputPath(str), even_lines_path: OutputPath(str)):
	with open(source_path, 'r') as reader:
		with open(odd_lines_path, 'w') as odd_writer:
			with open(even_lines_path, 'w') as even_writer:
				while True:
					line = reader.readline()
					if line == "":
						break
					odd_writer.write(line)
					line = reader.readline()
					if line == "":
						break
					even_writer.write(line)

def text_splitting_pipeline():
	text = '\n'.join(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
	split_text_task = split_text_lines(text)
	print_text(split_text_task.outputs['odd_lines'])
	print_text(split_text_task.outputs['even_lines'])

@func_to_container_op
def write_numbers(numbers_path: OutputPath(str), start: int = 0, count: int = 10):
	with open(numbers_path, 'w') as writer:
		for i in range(start, count):
			writer.write(str(i) + '\n')

# Reading and summing many numbers
@func_to_container_op
def sum_numbers(numbers_path: InputPath(str)) -> int:
	sum = 0
	with open(numbers_path, 'r') as reader:
		for line in reader:
			sum = sum + int(line)
	return sum

# Pipeline to sum 100000 numbers
def sum_pipeline(count: int = 100000):
	numbers_task = write_numbers(count=count)
	print_text(numbers_task.output)

	sum_task = sum_numbers(numbers_task.outputs['numbers'])
	print_text(sum_task.output)

def file_passing_pipelines():
	print_repeating_lines_pipeline()
	text_splitting_pipeline()
	sum_pipeline()

if __name__ == '__main__':
	# Compiling the pipeline
	kfp.compiler.Compiler().compile(file_passing_pipelines, __file__ + '.zip')
	kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
		file_passing_pipelines,
		arguments={},
		experiment_name=EXPERIMENT_NAME)