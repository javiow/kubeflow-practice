# kubeflow pipeline
# kfp를 관리할 수 있는 sdk 로드
import kfp

# 전역 변수 정의
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

# 함수 정의
def hello_world_component():
	ret = "Hello World!"
	print(ret)
	return ret

# 함수 -> 컴포넌트
@kfp.dsl.pipeline(name="hello_pipeline", description="Hello World Pipeline!")
def hello_world_pipeline():
	# 함수를 컴포넌트로 변경
	hello_world_op = kfp.components.func_to_container_op(hello_world_component)
	# 컴포넌트를 실행
	_ = hello_world_op()

if __name__ == "__main__":
	# zip 파일을 만들어서 같은 폴더에 zip 파일 하나 빌드(컴파일)
	kfp.compiler.Compiler().compile(hello_world_pipeline, 'hello-world-pipeline.zip')
	# 해당 파이프라인을 쿠베플로우 호스트에서 바로 실험
	kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
		hello_world_pipeline,
		arguments={},
		experiment_name="hello-world-experiment")