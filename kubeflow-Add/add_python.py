import kfp
from kfp import components
from kfp import dsl

EXPERIMENT_NAME = 'Add number pipeline' # Name of the experiment in the UI
BASE_IMAGE = "python:3.7"
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

@dsl.python_component(
	name='add_op',
	description='adds two numbers',
	base_image=BASE_IMAGE # you can define the base image here, or when you build in the next step.
)
def add(a: float, b: float) -> float:
	'''Calculates sum of two arguments'''
	print(a, '+', b, '=', a + b)
	return a + b

# Convert the function to a pipeline operation.
add_op = components.func_to_container_op(
	add,
	base_image=BASE_IMAGE, )
@dsl.pipeline(
	name='Calculation pipeline',
	description='A toy pipeline that performs arithmetic calculations.' )
def calc_pipeline(
	a: float = 0,
	b: float = 7
):
	#Passing pipeline parameter and a constant value as operation arguments
	add_task = add_op(a, 4) #Returns a dsl.ContainerOp class instance.
	#You can create explicit dependency between the tasks using xyz_task.after(abc_task)
	add_2_task = add_op(a, b)
	add_3_task = add_op(add_task.output, add_2_task.output)

if __name__ == "__main__":
	# Specify pipeline argument values
	arguments = {'a': '7', 'b': '8'}
	# Launch a pipeline run given the pipeline function definition
	kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
		calc_pipeline,
		arguments=arguments,
		experiment_name=EXPERIMENT_NAME)
		# The generated links below lead to the Experiment page and the pipeline run details page, respectively