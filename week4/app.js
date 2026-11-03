'use strict';

// Naver 단축 링크는 이 환경에서 확인하지 못했습니다.
// 다솔관은 학교 자료와 사용자가 알려 준 건물 이름으로 검색하며 식당의 정확한 위치는 아닙니다.
const placeConfig = {
  'place-0': {
    sourceUrl: 'https://naver.me/xG0qbUkd',
    mapUrl: 'https://www.google.com/maps?q=%EA%B0%80%ED%86%A8%EB%A6%AD%EB%8C%80%ED%95%99%EA%B5%90%20%EC%84%B1%EC%8B%AC%EA%B5%90%EC%A0%95%20%EB%8B%A4%EC%86%94%EA%B4%80%20%EA%B2%BD%EA%B8%B0%EB%8F%84%20%EB%B6%80%EC%B2%9C%EC%8B%9C%20%EC%9B%90%EB%AF%B8%EA%B5%AC%20%EC%A7%80%EB%B4%89%EB%A1%9C%2043&output=embed',
    mapNote: '다솔관 건물 이름으로 검색한 지도입니다. Google 검색 결과와 식당의 정확한 위치는 확인되지 않았습니다.'
  },
  'place-2': {
    sourceUrl: 'https://naver.me/539hXnME',
    mapUrl: 'https://www.google.com/maps/embed?pb=!1m3!2m1!1z6rCA7Yao66at64yA7ZWZ6rWQIOyEseyLrOq1kOygleq1reygnOq1kOulmOq0gA!5e1!3m2!1szh-CN!2sus!4v1793628354279!5m2!1szh-CN!2sus',
    mapNote: '제공받은 Google 지도입니다. 스터디룸의 정확한 위치는 확인되지 않았습니다.'
  },
  'place-1': {
    sourceUrl: 'https://naver.me/GbydUuk9',
    mapUrl: 'https://www.google.com/maps/embed?pb=!1m5!3m3!1m2!1s0x357cbcd317239033%3A0x6c91adb86f8948e1!2z6Z-p5Zu95aSp5Li75pWZ5aSn5a2m5qCh!5e1!3m2!1szh-CN!2sus!4v1793628507894!5m2!1szh-CN!2sus',
    mapNote: '제공받은 Google 지도입니다. 잔디밭의 정확한 위치는 확인되지 않았습니다.'
  }
};
const buttons = [...document.querySelectorAll('[data-place]')];
const places = [...document.querySelectorAll('.place')].map(section => ({
  id: section.id,
  name: section.querySelector('h2').textContent,
  description: section.querySelector('h2 + p').textContent,
  image: section.querySelector('img').getAttribute('src'),
  ...placeConfig[section.id],
  section
}));
const map = document.querySelector('#place-map');
const mapHeading = document.querySelector('#map-heading');
const mapStatus = document.querySelector('#map-status');
const mapPending = document.querySelector('#map-pending');
const mapSource = document.querySelector('#map-source');

function selectPlace(id) {
  const place = places.find(item => item.id === id);
  if (!place) return;
  places.forEach(item => { item.section.hidden = item.id !== id; });
  buttons.forEach(button => {
    button.setAttribute('aria-pressed', String(button.getAttribute('aria-controls') === id));
  });
  mapHeading.textContent = place.name + ' 지도';
  map.title = place.name + ' Google 지도';
  mapStatus.textContent = place.mapNote;
  mapSource.href = place.sourceUrl;
  map.hidden = !place.mapUrl;
  mapPending.hidden = Boolean(place.mapUrl);
  if (place.mapUrl) {
    if (map.getAttribute('src') !== place.mapUrl) map.setAttribute('src', place.mapUrl);
  } else {
    // 이전 장소의 지도가 남아 잘못된 위치처럼 보이지 않도록 제거합니다.
    map.removeAttribute('src');
  }
}

buttons.forEach(button => button.addEventListener('click', () => {
  selectPlace(button.getAttribute('aria-controls'));
}));
selectPlace('place-0');
