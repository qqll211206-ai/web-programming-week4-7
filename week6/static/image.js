'use strict';
const form = document.querySelector('#image-form');
const file = form.elements.image;
const button = document.querySelector('#fetch-button');
const status = document.querySelector('#status');
const times = document.querySelector('#times');
const original = document.querySelector('#original');
const result = document.querySelector('#result');
let originalUrl = null, resultUrl = null;

file.addEventListener('change', () => {
  if (originalUrl) URL.revokeObjectURL(originalUrl);
  originalUrl = null;
  original.hidden = true;
  if (file.files[0]) {
    originalUrl = URL.createObjectURL(file.files[0]);
    original.src = originalUrl;
    original.hidden = false;
  }
});

button.addEventListener('click', async () => {
  if (!form.reportValidity()) return;
  button.disabled = true;
  status.textContent = '처리 중입니다…';
  times.textContent = '';
  result.hidden = true;
  try {
    const started = performance.now();
    const response = await fetch(form.action, {
      method: 'POST',
      headers: { 'Accept': 'application/json' },
      body: new FormData(form)
    });
    if (!response.ok) {
      let message = '이미지를 처리하지 못했습니다.';
      try { message = (await response.json()).error || message; } catch {}
      throw new Error(message);
    }
    const blob = await response.blob();
    const elapsed = performance.now() - started;
    if (resultUrl) URL.revokeObjectURL(resultUrl);
    resultUrl = URL.createObjectURL(blob);
    result.src = resultUrl;
    result.hidden = false;
    const originalSize = response.headers.get('X-Original-Width') + ' × ' + response.headers.get('X-Original-Height');
    const processedSize = response.headers.get('X-Processed-Width') + ' × ' + response.headers.get('X-Processed-Height');
    times.textContent = '원본 ' + originalSize + ' px (EXIF 적용 전) · 처리 ' + processedSize +
      ' px · 알고리즘 ' + response.headers.get('X-Compute-Ms') + ' ms · 서버 ' +
      response.headers.get('X-Processing-Ms') + ' ms · 왕복 ' + elapsed.toFixed(1) + ' ms';
    status.textContent = '처리가 완료되었습니다.';
  } catch (error) {
    status.textContent = error.message || '요청에 실패했습니다.';
  } finally {
    button.disabled = false;
  }
});
window.addEventListener('pagehide', () => {
  if (originalUrl) URL.revokeObjectURL(originalUrl);
  if (resultUrl) URL.revokeObjectURL(resultUrl);
});
