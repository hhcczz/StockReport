# StockReport
> Toss에서 크롤링해 주식 정보 보기 프로그램

<br>

# 💻 프로그램 실행 화면

<table align="center">
  <td align ="center">
    <img src="https://github.com/user-attachments/assets/e705f639-6640-4c8d-8fff-b06bcbb6fb2b" width = "954px"/><br/>
    <sub><strong>현재 주식 정보 및 관심 종목 정보</strong></sub>
  </td>
</table>

<table align="center">
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/99f28e47-57e6-4058-9a39-bb0c340e547b" width="300px"/><br/>
      <sub><strong>국내</strong></sub>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/4727a4f6-02ae-4a4c-8856-f841bd449340" width="300px"/><br/>
      <sub><strong>해외</strong></sub>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/50c53025-0d83-4469-a92e-4c1261dfb794" width="300px"/><br/>
      <sub><strong>ETF</strong></sub>
    </td>
  </tr>
</table>

<br>

# 📈 프로젝트 개요

- **주식의 핵심 정보**인 종목, 가격, 등락(￦), 등락(%)을 한눈에 보기 쉽게 시각화함
- **관심 종목만 선택하여 이미지로 추출** 가능하며, 프로그램 내에서는 실시간 시세 확인 기능 제공
- **개발기간**: 2024.08.02 ~ 2024.08.23 ( 22일 )
- **개발인원**: 2명
- **형상관리**: Github

<br>

# 🎯 제작 의도

- 주식 데이터 탐색 중, **과도한 정보 노출과 불필요한 인터랙션(로그인, 클릭 등)** 없이  
  **핵심 지표(종목명, 현재가, 등락폭/등락률)**만 빠르게 조회할 수 있는 경량 도구의 필요성을 느꼈습니다.

- 기존 서비스들은 종목 탐색 시 **사용자 로그인을 요구하거나 개별 종목을 일일이 클릭해야 하는 번거로움**이 존재했으며,  
  **사용자 지정 관심 종목을 한 화면에서 직관적으로 확인하는 데 한계**가 있었습니다.

- 특히, **일별 등락률은 쉽게 확인되지만, 특정 시간대 기준 가격을 정적으로 기록하거나 비교하기 위한 수단이 부족**하다는 점에서 착안하여,  
  **이미지 추출 및 시점 고정형 데이터 확인이 가능한 실시간 주식 시세 뷰어**를 구현하게 되었습니다.

<br>

# 🛠️ 개발 환경
+ Visual Studio Code
+ Python 3.12.4 ('base') conda
+ UTF-8
+ PC

<br>

# 📌 개발 특징 및 최적화

- Toss 주식 API를 사용하여 **안정적이고 실시간 반영이 가능한 가격 데이터 수신**  
- **고정 종목 리스트 기반으로 UI 요소를 사전에 구성**하여 불필요한 렌더링을 방지  
- 종목별 이미지 요청 시 **중복 호출을 방지하고, 캐시 메모리를 활용**해 이미지 불러오기 속도 최적화  
- 별도의 외부 라이브러리 없이, **Python 기본 모듈만으로 이미지 생성 및 저장 구현**
