/**
 * Theme Toggle and Image Update Script
 * =====================================
 * 
 * This script dynamically updates the theme of a webpage between light and dark modes based on
 * user preferences or system settings. It also modifies the sources of images and lightbox
 * href attributes to match the current theme.
 * 
 * Author: Firas AlShafei
 * Email: f.alshafei@gmail.com
 * Version: 1.0.0
 * 
 * Functionality:
 * --------------
 * - Dynamically changes the theme based on user preferences or system settings.
 * - Updates image sources to match the current theme by appending or removing '_dark' in the URL.
 * - Updates lightbox href attributes to match the current theme.
 * - Provides a debug mode for logging actions to the console.
 * - Includes helper functions for controlled logging, theme state retrieval, and lightbox reloading.
 * 
 * Usage:
 * ------
 * Replaces the default dark-images.js script from the mkdocs-build-plantuml-plugin.
 */

// Set this flag to true for debugging output, false to suppress logs
const DEBUG = false;

/**
 * Helper function for controlled logging.
 * @param {string} message - The message to log.
 */
function log(message) {
  if (DEBUG) {
    console.log(message);
  }
}

/**
 * Retrieves the current theme state based on the data attribute on the body.
 * @returns {string} - The current theme state ('dark', 'light', or system preference).
 */
function getCurrentThemeState() {
  const colorScheme = document.body.getAttribute('data-md-color-media');
  log(`🌈 Current data-md-color-media value: ${colorScheme}`);

  switch (colorScheme) {
    case '(prefers-color-scheme: dark)':
      return 'dark';
    case '(prefers-color-scheme: light)':
      return 'light';
    case '(prefers-color-scheme)':
    default:
      const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      log(`🌐 System preference: ${systemPreference}`);
      return systemPreference;
  }
}

/**
 * Updates the theme based on the provided mode.
 * @param {string} mode - The theme mode ('dark' or 'light').
 * @param {NodeListOf<HTMLImageElement>} darkables - The images to update.
 */
function updateTheme(mode, darkables) {
  log(`🔄 Updating theme to: ${mode}`);
  if (mode === 'dark') {
    fromLightToDark(darkables);
    log('🌒 Dark mode is on.');
  } else {
    fromDarkToLight(darkables);
    log('☀️ Light mode is on.');
  }
}

/**
 * Switches images and lightbox hrefs to dark mode by appending '_dark' to their src or href.
 * @param {NodeListOf<HTMLImageElement>} images - The images to update.
 */
function fromLightToDark(images) {
  log('🌑 Switching images to dark mode...');
  images.forEach(image => {
    if (!image.src.includes('_dark')) {
      var idx = image.src.lastIndexOf('.');
      if (idx > -1) {
        var add = "_dark";
        image.src = [image.src.slice(0, idx), add, image.src.slice(idx)].join('');
      }
    }
    // Update the lightbox href if it exists
    const link = image.closest('a.glightbox');
    if (link && !link.href.includes('_dark')) {
      var idx = link.href.lastIndexOf('.');
      if (idx > -1) {
        var add = "_dark";
        link.href = [link.href.slice(0, idx), add, link.href.slice(idx)].join('');
      }
    }
  });
}

/**
 * Switches images and lightbox hrefs to light mode by removing '_dark' from their src or href.
 * @param {NodeListOf<HTMLImageElement>} images - The images to update.
 */
function fromDarkToLight(images) {
  log('🌞 Switching images to light mode...');
  images.forEach(image => {
    image.src = image.src.replace("_dark", "");
    // Update the lightbox href if it exists
    const link = image.closest('a.glightbox');
    if (link) {
      link.href = link.href.replace("_dark", "");
    }
  });
}

/**
 * Handles changes in theme preference (system or manual).
 */
function handleThemeChange() {
  log('🎨 Theme preference changed.');
  var darkables = document.querySelectorAll('img[src$="darkable"]');
  updateTheme(getCurrentThemeState(), darkables);
  reloadLightbox(); 
}

// Initial check for system preference and update the theme accordingly
(function initialThemeCheck() {
  var darkables = document.querySelectorAll('img[src$="darkable"]');
  updateTheme(getCurrentThemeState(), darkables);
  reloadLightbox(); 
})();

// Set up event listener for system color scheme preference changes
const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
darkModeMediaQuery.addEventListener('change', handleThemeChange);

// Set up event listeners for the theme toggle inputs
document.querySelectorAll('input[name="__palette"]').forEach(input => {
  input.addEventListener('change', handleThemeChange);
});

/**
 * Reloads the lightbox to update the image references.
 */
function reloadLightbox() {
  if (typeof GLightbox !== 'undefined') {
    log('🔄 Reloading lightbox...');
    document$.subscribe(() => { lightbox.reload(); });
  } else {
    log('↪️ GLightbox is not defined, skipping');
  }
}
