import glob
import pytest
import importlib.util
import sys, os
from airflow.models import DAG, Variable
from airflow.utils.dag_cycle_tester import check_cycle

# 테스트 시,작성한 py 모듈을 import할 수 있도록 dags 폴더를 시스템에 등록
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../dags')

DAG_PATH = os.path.join(os.path.dirname(__file__),"..","dags/*.py")

DAG_FILES = glob.glob(DAG_PATH)

# Mocking을 위한 Fixture 생성
@pytest.fixture(autouse=True) # autouse=True로 하여 테스트 시 모든 DAG에 일괄 적용
def airflow_variables():
    return {
        "kakao_api_key_dabang": "mock_url",
        "dabang_base_url": "mock_url",
    }

# 발견된 모든 파이썬 파일에 대해 테스트 진행
@pytest.mark.parametrize("dag_file", DAG_FILES)
def test_dag_integrity(airflow_variables, dag_file, monkeypatch): # DAG 무결성 검사 - import Error만 고려
    
    # Monkeypatch를 통해 런타임 중에 소스 코드 내용을 변경
    # Airflow variable을 지정한 fixture로 변경
    def mock_get(*args, **kwargs):
        mocked_dict = airflow_variables
        return mocked_dict.get(args[0])

    monkeypatch.setattr(Variable, "get", mock_get)
    
    # DAG 파일명 분리
    module_name, _ = os.path.splitext(dag_file)
    # 파일 경로 추출
    module_path = os.path.join(DAG_PATH, dag_file)
    # 파일 로드
    mod_spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(module)
    
    # 파일에 DAG 객체가 존재한다면 유효성 검증을 위해 보관
    dag_objects = [var for var in vars(module).values() if isinstance(var, DAG)]
    
    # DAG 객체가 존재하는 경우에 대해서만 DAG import error 검증
    if any(isinstance(var, DAG) for var in vars(module).values()) :
        assert dag_objects
    
    # DAG 객체에 대한 순환 주기가 있는지 확인
    for dag in dag_objects:
        check_cycle(dag)