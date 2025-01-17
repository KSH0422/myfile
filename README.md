[[명품정하기.py]]
해당 코드는 명품 수입에 관련된 가격 설정 프로그램
프로그램은 이렇게 돌아갑니다.
1.프로그램을 실행하면 거래 방법을 선택합니다. (DDP 또는 EXW)
2.엑셀 선택창이 나오는데 거래처에서 받은 엑셀 중 가공이 필요한 엑셀을 선택
3.그 후 내가 수입해야하는 브랜드만 선택해서 ADD 버튼을 누릅니다.
4.환율과 마진을 설정하고 IVA 여부를 선택하고 OK버튼을 누릅니다.
5.이제 프로그램이 실행되고 선택된 브랜드의 모든 제품의 가격이 설정한 환율,세금,마진에 알맞게 계산되어서 나옵니다.

[[바이비트 api 차트그리기, 주문창 불러오기, 주문하기]]
바이비트 api를 통해서 실시간으로 비트코인의 가격을 받아와 차트를 그리고 비트코인의 가격을 볼수있다.
주문창에서 롱,숏을 설정할수있고 주문까지 가능(아직 계발중)
추후에는 매수,매도 시그널까지 추가 개발

[[강수계급 예측]]
기상청의 빅데이터날씨콘테스트 엑스트라트리를 이용한 앙상블모델 개발
데이터전처리,변수선택,하이퍼파라미터조정,모델평가

[[암 분류]]
처음에 이 프로젝트에 들어갔을 때, 수많은 유전자 데이터와 다양한 돌연변이 유형을 어떻게 처리해야 할지 막막했지만, 하나씩 풀어나가면서 제 나름대로의 해답을 찾아갔습니다.

처음에는 WT, Synonymous, Nonsynonymous, Frameshift 같은 다양한 돌연변이 유형을 구분하고, 이를 라벨 인코딩하는 데 집중했습니다. 이 과정을 통해 각 변이의 특성을 반영한 데이터를 만들 수 있었고, 다음 단계로는 이진 분류를 통해 데이터를 정리했습니다. 단순히 데이터를 나누는 것에 그치지 않고, 그 뒤에 숨어 있는 패턴을 발견하는 것이 저의 목표였습니다.

이 과정에서 마주한 도전 중 하나는 데이터 불균형이었습니다. 암 발병 데이터의 클래스 간 불균형이 심각했기 때문에, 클래스 가중치를 적용해 이 문제를 해결하고자 했습니다. 또한, 단일 모델로는 한계가 있다고 판단해 XGBoost, LightGBM 등의 다양한 모델을 활용하여 스태킹 방식을 도입했습니다. 결과적으로, 이러한 방식은 예측 성능을 크게 향상시키는 데 도움이 되었고, 제 자신도 데이터의 잠재력에 대해 새로운 시각을 얻게 되었습니다.

이 모든 과정에서 GPU 병렬 처리를 통해 대규모 데이터를 효율적으로 처리할 수 있었습니다. 두 개의 T4 GPU를 동시에 사용하여 학습 시간을 줄이고, 최종적으로는 LightGBM 메타 모델을 통해 더욱 정확한 결과를 도출할 수 있었습니다. 이런 경험을 통해 데이터를 다루는 과정에서 가장 중요한 것은 인내심과 끝없는 도전이라는 것을 다시금 깨달았습니다.

이 프로젝트를 마치면서, 유전자 데이터를 활용한 분석이 얼마나 많은 가능성을 내포하고 있는지 실감했습니다. 그리고 무엇보다, 데이터가 가진 힘을 통해 인간의 생명을 구할 수 있는 길을 찾는다는 사실이 저에게는 큰 동기부여가 되었습니다. 앞으로도 저는 이 분야에서 계속해서 성장해 나가고 싶습니다. 분석하고, 개선하고, 도전하는 과정을 반복하면서 더욱 깊이 있는 인사이트를 찾아가고 싶습니다.
