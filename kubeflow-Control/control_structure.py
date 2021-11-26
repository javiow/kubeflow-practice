EXPERIMENT_NAME = 'Control Structure' # Name of the experiment in the UI
BASE_IMAGE = "python:3.7"
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

import kfp
from kfp import dsl
from kfp.components import func_to_container_op, InputPath, OutputPath

# 최소값과 최대값 사이의 랜덤값을 뽑는 컴포넌트
@func_to_container_op
def get_random_int_op(minimum: int, maximum: int) -> int:
	"""Generate a random number between minimum and maximum (inclusive)."""
	import random
	result = random.randint(minimum, maximum)
	print(result)
	return result

# 동전 던지기를 해서 위/아래를 정해주는 컴포넌트
@func_to_container_op
def flip_coin_op() -> str:
	"""Flip a coin and output heads or tails randomly."""
	import random
	result = random.choice(['heads', 'tails'])
	print(result)
	return result
	
# 메세지를 출력해주는 컴포넌트
@func_to_container_op
def print_op(message: str):
	"""Print a message."""
	print(message)


@dsl.pipeline(
	name='Conditional execution pipeline',
	description='Shows how to use dsl.Condition().' )
def flipcoin_pipeline():
	# 앞면/뒷면 값
	flip = flip_coin_op()
	# 앞면이 나왔을 때
	with dsl.Condition(flip.output == 'heads'):
		random_num_head = get_random_int_op(0, 9)
		with dsl.Condition(random_num_head.output > 5):
			print_op('heads and %s > 5!' % random_num_head.output)
		with dsl.Condition(random_num_head.output <= 5):
			print_op('heads and %s <= 5!' % random_num_head.output)

	# 뒷면이 나왔을 때
	with dsl.Condition(flip.output == 'tails'):
		random_num_tail = get_random_int_op(10, 19)
		with dsl.Condition(random_num_tail.output > 15):
			print_op('tails and %s > 15!' % random_num_tail.output)
		with dsl.Condition(random_num_tail.output <= 15):
			print_op('tails and %s <= 15!' % random_num_tail.output)

# %%
@func_to_container_op
def fail_op(message):
	"""Fails."""
	import sys
	print(message)
	sys.exit(1)

@dsl.pipeline(
	name='Conditional execution pipeline with exit handler',
	description='Shows how to use dsl.Condition() and dsl.ExitHandler().' )
def flipcoin_exit_pipeline():
	exit_task = print_op('Exit handler has worked!')
	with dsl.ExitHandler(exit_task):
		flip = flip_coin_op()
		with dsl.Condition(flip.output == 'heads'):
			random_num_head = get_random_int_op(0, 9)
			with dsl.Condition(random_num_head.output > 5):
				print_op('heads and %s > 5!' % random_num_head.output)
			with dsl.Condition(random_num_head.output <= 5):
				print_op('heads and %s <= 5!' % random_num_head.output)
	
		with dsl.Condition(flip.output == 'tails'):
			random_num_tail = get_random_int_op(10, 19)
			with dsl.Condition(random_num_tail.output > 15):
				print_op('tails and %s > 15!' % random_num_tail.output)
			with dsl.Condition(random_num_tail.output <= 15):
				print_op('tails and %s <= 15!' % random_num_tail.output)

		with dsl.Condition(flip.output == 'tails'):
			fail_op(message="Failing the run to demonstrate that exit handler still gets executed.")

if __name__ == '__main__':
 # Compiling the pipeline
 kfp.compiler.Compiler().compile(flipcoin_exit_pipeline, __file__ + '.zip')
 kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
	 flipcoin_exit_pipeline,
	 arguments={},
	 experiment_name=EXPERIMENT_NAME)