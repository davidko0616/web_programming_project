for (let i = 0; i < numSlices; i++) {
  const slice = document.createElement('div');
  slice.classList.add('slice');

  const sliceHeight = 100 / numSlices;
  slice.style.top = `${sliceHeight * i}%`;

  // This is the fix: offset background Y position
  slice.style.backgroundPosition = `center ${sliceHeight * i}%`;

  slideshow.appendChild(slice);
  slices.push(slice);
}
