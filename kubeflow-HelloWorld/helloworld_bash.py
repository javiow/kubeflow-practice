import kfp
from kfp import dsl

BASE_IMAGE = "library/bash:4.4.23"
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

def echo_op():
	return dsl.ContainerOp(
		name="echo",
		image=BASE_IMAGE,
		# 쉘 스크립트 실행
		command=["sh", "-c"],
		# 쉘 스크립트에 명령
		arguments=['echo "hello world"'],
	)

@dsl.pipeline(name="hello_world_bash_pipeline", description="A hello world pipeline.")
def hello_world_bash_pipeline():
	# 이 파이프라인은 위 컴포넌트를 실행
	echo_task = echo_op()

if __name__ == "__main__":
	kfp.compiler.Compiler().compile(hello_world_bash_pipeline, __file__ + ".zip")
	kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
	hello_world_bash_pipeline,
	arguments={},
	experiment_name="hello-world-bash-experiment",
	)