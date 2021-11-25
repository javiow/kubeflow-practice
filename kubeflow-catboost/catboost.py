import kfp
from kfp import components

EXPERIMENT_NAME = 'CatBoost pipeline'        # Name of the experiment in the UI
KUBEFLOW_HOST = "http://127.0.0.1:31380/pipeline"

# load_component_from_url: url 경로에 있는 yaml 파일을 바로 컴포넌트로 변환
# 시카고 택시 데이터셋을 가져오는 컴포넌트
chicago_taxi_dataset_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/e3337b8bdcd63636934954e592d4b32c95b49129/components/datasets/Chicago%20Taxi/component.yaml')
# 판다스 데이터프레임을 csv파일로 변환해주는 컴포넌트
pandas_transform_csv_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/e69a6694/components/pandas/Transform_DataFrame/in_CSV_format/component.yaml')

# 분류 학습 모델 컴포넌트
catboost_train_classifier_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/Train_classifier/from_CSV/component.yaml')
# 회귀 학습 모델 컴포넌트
catboost_train_regression_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/Train_regression/from_CSV/component.yaml')
# 클래스를 예측하는 컴포넌트
catboost_predict_classes_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/Predict_classes/from_CSV/component.yaml')
# 값을 예측하는 컴포넌트
catboost_predict_values_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/Predict_values/from_CSV/component.yaml')
# 클래스 확률분포를 예측하는 컴포넌트
catboost_predict_class_probabilities_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/Predict_class_probabilities/from_CSV/component.yaml')

# 애플 형태로 모델 변경하는 컴포넌트
catboost_to_apple_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/convert_CatBoostModel_to_AppleCoreMLModel/component.yaml')
# 오닉스 형태로 모델 변경하는 컴포넌트
catboost_to_onnx_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/f97ad2/components/CatBoost/convert_CatBoostModel_to_ONNX/component.yaml')



def catboost_pipeline():
    # Query형태로 시카고 택시 데이터를 가져옴
    training_data_in_csv = chicago_taxi_dataset_op(
        where='trip_start_timestamp >= "2019-01-01" AND trip_start_timestamp < "2019-02-01"',
        select='tips,trip_seconds,trip_miles,pickup_community_area,dropoff_community_area,fare,tolls,extras,trip_total',
        limit=10000,
    ).output

    # 조건에 맞게 데이터를 변형
    training_data_for_classification_in_csv = pandas_transform_csv_op(
        table=training_data_in_csv,
        transform_code='''df.insert(0, "was_tipped", df["tips"] > 0); del df["tips"]''',
    ).output

    # 회귀 모델을 학습
    catboost_train_regression_task = catboost_train_regression_op(
        training_data=training_data_in_csv,
        loss_function='RMSE',
        label_column=0,
        num_iterations=200,
    )

    # 학습된 모델 불러오기
    regression_model = catboost_train_regression_task.outputs['model']

    # 분류 모델 학습
    catboost_train_classifier_task = catboost_train_classifier_op(
        training_data=training_data_for_classification_in_csv,
        label_column=0,
        num_iterations=200,

    )

    # 학습된 모델 불러오기
    classification_model = catboost_train_classifier_task.outputs['model']

    evaluation_data_for_regression_in_csv = training_data_in_csv
    evaluation_data_for_classification_in_csv = training_data_for_classification_in_csv

    # 값 예측
    catboost_predict_values_op(
        data=evaluation_data_for_regression_in_csv,
        model=regression_model,
        label_column=0,
    )

    # 클래스 예측
    catboost_predict_classes_op(
        data=evaluation_data_for_classification_in_csv,
        model=classification_model,
        label_column=0,
    )

    # 확률 분포 예측
    catboost_predict_class_probabilities_op(
        data=evaluation_data_for_classification_in_csv,
        model=classification_model,
        label_column=0,
    )

    # 애플 형태로 변경
    catboost_to_apple_op(regression_model)
    catboost_to_apple_op(classification_model)

    # 오닉스 형태로 변경
    catboost_to_onnx_op(regression_model)
    catboost_to_onnx_op(classification_model)


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(catboost_pipeline, __file__ + '.zip')
    kfp.Client(host=KUBEFLOW_HOST).create_run_from_pipeline_func(
        catboost_pipeline,
        arguments={},
        experiment_name=EXPERIMENT_NAME)