# LoopUs
## 일상속 포트폴리오 루프어스
![screenshot](./img/loopus.png)

 [google play store link](https://play.google.com/store/apps/details?id=com.loopus.loopus)

 [app store link](https://apps.apple.com/kr/app/%EB%A3%A8%ED%94%84%EC%96%B4%EC%8A%A4/id1603358083)

<h4>
사업 소개
<ul>
<li>2022년 인천대학교 창업동아리 활동</li>
<li>학생의 mydata를 활용한 학생과 기업간의 구인구직 플랫폼</li>
<li>취업시장의 판도가 공채에서 상시채용으로 변하고 있음</li>
<li>하지만 아직 취업시장에 뛰어들 학생들은 상시채용에 대해 어색함</li>
<li>기존의 SNS 플랫폼을 활용하여 학생들에 친근하게 다가감</li>
</ul>
</h4>

<h4>
사용 기술
<ul>
<li>gunicorn을 이용해 서비스</li>
<li>elasticsearch 엔진을 이용하여 검색기능 구현</li>
<li>redis를 이용하여 학교 이메일 기반 인증절차 구현</li>
<li>gunicorn, elasticsearch, redis를 linux의 system daemon에서 관리</li>
<li>aws의 ec2, rds, s3 이용</li>
<li>사용자가 업로드한 파일이나, 이미지를 s3와 연동하여 bucket에 저장</li>
<li>프론트는 dart의 flutter를 사용, 알람기능을 fcm으로 구현</li>
<li>apscheduler를 사용하여 매일 오후 10시 사용자들의 랭크를 계산</li>
<li>매일 오전 7시 주요 tag에 대해 뉴스, 영상, 블로그 글을 검색하여 사용자들에게 보여줌</li>


</ul>
</h4>