// Handle Material 9.x theme toggle for diagram images
function updateDiagramImages() {
  const scheme = document.body.getAttribute('data-md-color-scheme');
  const darkables = document.querySelectorAll('img[src$="darkable"]');

  if (scheme === 'slate') {
    fromLightToDark(darkables);
  } else {
    fromDarkToLight(darkables);
  }
}

function fromLightToDark(images) {
  images.forEach(image => {
    if (!image.src.includes('_dark.')) {
      const idx = image.src.lastIndexOf('.');
      if (idx > -1) {
        image.src = [image.src.slice(0, idx), '_dark', image.src.slice(idx)].join('');
      }
    }
  });
}

function fromDarkToLight(images) {
  images.forEach(image => {
    image.src = image.src.replace('_dark.', '.');
  });
}

// Initial check on page load
document.addEventListener('DOMContentLoaded', updateDiagramImages);

// Watch for theme changes via MutationObserver
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-md-color-scheme') {
      updateDiagramImages();
    }
  });
});

observer.observe(document.body, { attributes: true });
