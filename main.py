import time
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# 웹 요소를 찾기 위한 locator 정의 (특정 웹 요소를 찾기 위해 사용되는 식별자 정의)
SEARCH_BOX = (By.CSS_SELECTOR, '#query')  # 검색창
SEARCH_BUTTON = (By.CSS_SELECTOR, '#search-btn')  # 검색 버튼
SEARCH_RESULT = (By.CSS_SELECTOR, '.list_news > li')  # 검색 결과 리스트의 첫 번째 항목
NO_RESULT_MESSAGE = (By.CSS_SELECTOR, '#notfound > div.not_found02 > p')  # 검색 결과 없음 메시지 출력 영역

@pytest.fixture(scope="function")  # pytest에서 fixture를 정의할 때 사용하는 데코레이터로, fixture의 범위를 지정하는 역할(특정 설정이나 초기화 작업을 수행할 수 있는 함수를 정의)
def driver(request):  # driver라는 이름의 함수를 정의, request는 pytest의 내장 객체로 현재 테스트 요청에 대한 정보를 포함
    # 각 테스트 함수마다 새로운 Chrome 웹드라이버 인스턴스를 생성
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)  # 암시적 대기 시간 설정 (10초)
    
    def teardown():
        # 테스트가 완료된 후 리소스를 해제하거나, 결과를 기록하는 데 사용
        # 테스트 종료 시 실행되는 teardown 함수
        # 스크린샷을 캡처하여 Allure 리포트에 첨부
        allure.attach(driver.get_screenshot_as_png(), name="Screenshot", attachment_type=allure.attachment_type.PNG)
        driver.quit()  # 브라우저 종료
    
    request.addfinalizer(teardown)  # teardown 함수를 테스트 종료 시 실행하도록 등록
    return driver

@pytest.fixture(scope="function")
def naver_home(driver):
    # 각 테스트 함수마다 네이버 홈페이지로 이동
    driver.get('https://www.naver.com/')
    return driver

@allure.feature('Naver 접속 테스트')
@allure.story('TC_001 - Naver 사이트에 접속')
def test_naver_access(naver_home):
    # 네이버 홈페이지 URL 확인
    naver_url = naver_home.current_url
    assert naver_url == 'https://www.naver.com/', "Naver 접속 실패"  # assert 문은 주어진 조건이 True일 때는 아무런 동작도 하지 않고, False일 경우에는 AssertionError를 발생시킴. 주로 디버깅이나 테스트에서 사용

@allure.feature('검색 기능 테스트(비유효)')
@allure.story('TC_002 - Naver에서 비유효한 단어 검색')
def test_search_invalid_word(naver_home):
    # 검색창 요소가 나타날 때까지 대기 후 클릭
    search_box = WebDriverWait(naver_home, 10).until(EC.presence_of_element_located(SEARCH_BOX))
    search_box.click()
    search_box.send_keys('28tu9w8g')  # 비유효한 검색어 입력
    
    naver_home.find_element(*SEARCH_BUTTON).click()  # 검색 버튼 클릭
    
    # 검색 결과 없음 메시지 노출 영역이 페이지에 나타날 때까지 대기
    search_result_element = WebDriverWait(naver_home, 10).until(EC.presence_of_element_located(NO_RESULT_MESSAGE))
    search_result_text = search_result_element.text.strip()  # 검색 결과 텍스트 가져오기 및 공백 제거, .strip() 메서드는 문자열의 앞뒤에 있는 공백(스페이스, 탭, 줄바꿈 등)을 제거
    
    # 검색 결과 텍스트에 입력한 검색어('28tu9w8g')와 "검색결과가 없습니다" 문구가 포함되어 있는지 확인
    assert '28tu9w8g' in search_result_text and '검색결과가 없습니다' in search_result_text, f"비유효한 단어 검색 실패. 실제 결과: '{search_result_text}'"

@allure.feature('검색 기능 테스트(유효)')
@allure.story('TC_003 - Naver에서 사과 검색')
def test_search_apple(naver_home):
    # 검색창 요소가 나타날 때까지 대기 후 클릭
    search_box = WebDriverWait(naver_home, 10).until(EC.presence_of_element_located(SEARCH_BOX))
    search_box.click()
    search_box.send_keys('사과')  # 유효한 검색어 입력
    
    naver_home.find_element(*SEARCH_BUTTON).click()  # 검색 버튼 클릭, *는 언팩킹(unpacking) 연산자로, 튜플이나 리스트의 요소를 개별적인 인자로 전달하는 데 사용(SEARCH_BUTTON은 튜플 형태로 정의된 변수), find_element 메서드는 find_element(By.CSS_SELECTOR, 'button.search')와 같이 호출됨
    
    # 검색 결과가 표시될 때까지 대기 후 확인
    search_result = WebDriverWait(naver_home, 10).until(EC.visibility_of_element_located(SEARCH_RESULT)).is_displayed()
    assert search_result, "사과 검색 실패"

@allure.feature('Naver 검색 결과 테스트')
@allure.story('TC_004 - Naver 검색 결과에서 첫 번째 뉴스 클릭')
def test_search_first_news(naver_home):
    # 검색창 요소가 나타날 때까지 대기 후 클릭
    search_box = WebDriverWait(naver_home, 10).until(EC.presence_of_element_located(SEARCH_BOX))
    search_box.click()
    search_box.send_keys('사과')  # 검색어 입력

    naver_home.find_element(*SEARCH_BUTTON).click()  # 검색 버튼 클릭

    try:
        # 첫 번째 뉴스 항목이 클릭 가능할 때까지 대기 후 클릭
        first_news = WebDriverWait(naver_home, 10).until(EC.element_to_be_clickable(SEARCH_RESULT))
        first_news.click()

        # 새 창이 열릴 때까지 대기 (최대 10초)
        # Selenium을 사용하여 특정 조건이 충족될 때까지 대기하는 코드, 이 코드의 목적은 현재 브라우저 창의 수가 2가 될 때까지 기다리는 것
        WebDriverWait(naver_home, 10).until(EC.number_of_windows_to_be(2))

        # 모든 창 핸들 가져오기(핸들: 각 브라우저 창이나 탭을 식별하는 고유한 문자열 값)
        handles = naver_home.window_handles

        # 새로 열린 창으로 전환 (현재 작업할 창을 전환하기 위해 사용)
        # handles[-1]은 handles 리스트의 마지막 요소를 의미. -1은 가장 최근에 열린 창
        naver_home.switch_to.window(handles[-1])

        # URL이 네이버 홈이 아닌 다른 페이지로 변경될 때까지 대기 (최대 10초),  페이지 이동이나 상태 변화를 확인하는 데 유용
        WebDriverWait(naver_home, 10).until(
            lambda driver: driver.current_url != 'https://www.naver.com/'
        )

        # 현재 URL 확인
        current_url = naver_home.current_url
        
        # 허용되는 URL 패턴 목록
        allowed_patterns = ['news.naver.com', 'n.news.naver.com', 'sports.news.naver.com', 'ytn.co.kr']
        
        # 현재 URL이 허용된 패턴 중 하나를 포함하는지 확인
        # allowed_patterns 리스트에 있는 각 패턴에 대해 current_url에 그 패턴이 포함되어 있는지를 체크
        assert any(pattern in current_url for pattern in allowed_patterns), f"첫 번째 뉴스 클릭 실패. 현재 URL: {current_url}"

    except Exception as e:  # try 블록에서 발생한 모든 예외를 잡기 위한 코드, Exception 클래스는 모든 예외의 기본 클래스이므로 발생할 수 있는 모든 예외를 처리
        # 예외 발생 시 스크린샷 캡처하여 Allure 리포트에 첨부
        allure.attach(naver_home.get_screenshot_as_png(), name="Screenshot on Failure", attachment_type=allure.attachment_type.PNG)
        raise e  # 예외를 다시 발생시켜 테스트 실패 처리