(function(selector, options) {
    const element = document.querySelector(selector);
    if (!element) return {error: 'Element not found'};
    
    const result = {
        images: [],
        background_images: [],
        fonts: {
            font_faces: []
        },
        icons: [],
        stylesheets: [],
        videos: [],
        audio: [],
        loaded_resources: []
    };
    
    const includeImages = $INCLUDE_IMAGES;
    const includeBackgrounds = $INCLUDE_BACKGROUNDS;
    const includeFonts = $INCLUDE_FONTS;
    const fetchExternal = $FETCH_EXTERNAL;
    
    function addUnique(list, item, key) {
        const value = item[key];
        if (!value || list.some(existing => existing[key] === value)) return;
        list.push(item);
    }

    function extractCssUrls(value) {
        if (!value || value === 'none') return [];
        const urls = [];
        const regex = /url\(["']?([^"')]+)["']?\)/g;
        let match;
        while ((match = regex.exec(value)) !== null) {
            urls.push(match[1]);
        }
        return urls;
    }

    function extractSrcset(srcset) {
        if (!srcset) return [];
        return srcset
            .split(',')
            .map(part => part.trim().split(/\s+/)[0])
            .filter(Boolean);
    }

    function absolutize(url, base) {
        try {
            return new URL(url, base || document.baseURI).href;
        }
        catch (e) {
            return url;
        }
    }

    function firstAttr(el, names) {
        for (const name of names) {
            const value = el.getAttribute(name);
            if (value) return value;
        }
        return '';
    }

    function elementPath(el) {
        if (!el || !el.tagName) return selector;
        const parts = [];
        let current = el;
        while (current && current !== document.documentElement && parts.length < 6) {
            let part = current.tagName.toLowerCase();
            if (current.id) {
                part += `#${current.id}`;
                parts.unshift(part);
                break;
            }
            if (current.className && typeof current.className === 'string') {
                const classes = current.className.trim().split(/\s+/).slice(0, 2).join('.');
                if (classes) part += `.${classes}`;
            }
            parts.unshift(part);
            current = current.parentElement;
        }
        return parts.join(' > ') || selector;
    }

    // Extract images
    if (includeImages) {
        const images = element.matches('img') ? [element] : Array.from(element.querySelectorAll('img'));
        images.forEach(img => {
            const rawSrc = firstAttr(img, [
                'src',
                'data-src',
                'data-original',
                'data-lazy-src',
                'data-srcset',
                'data-background-image'
            ]);
            const sourceUrl = img.currentSrc || img.src || rawSrc;
            if (sourceUrl) {
                addUnique(result.images, {
                    src: absolutize(sourceUrl),
                    alt: img.alt,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    loading: img.loading,
                    srcset: img.srcset || '',
                    srcset_urls: extractSrcset(img.srcset).map(url => absolutize(url)),
                    lazy_src: rawSrc ? absolutize(rawSrc) : '',
                    element_selector: elementPath(img)
                }, 'src');
            }
        });

        element.querySelectorAll('source[srcset]').forEach(source => {
            extractSrcset(source.srcset).forEach(url => {
                addUnique(result.images, {
                    src: absolutize(url),
                    alt: '',
                    width: 0,
                    height: 0,
                    loading: '',
                    srcset: source.srcset,
                    srcset_urls: extractSrcset(source.srcset).map(url => absolutize(url)),
                    element_selector: elementPath(source)
                }, 'src');
            });
        });

        element.querySelectorAll('svg image[href], svg image[xlink\\:href], use[href], use[xlink\\:href]').forEach(svgAsset => {
            const href = svgAsset.getAttribute('href') || svgAsset.getAttribute('xlink:href');
            if (href && !href.startsWith('#')) {
                addUnique(result.images, {
                    src: absolutize(href),
                    alt: '',
                    width: 0,
                    height: 0,
                    loading: '',
                    srcset: '',
                    srcset_urls: [],
                    element_selector: elementPath(svgAsset)
                }, 'src');
            }
        });
    }
    
    // Extract background images
    if (includeBackgrounds) {
        const backgroundElements = [element, ...element.querySelectorAll('*')];
        backgroundElements.forEach(bgElement => {
            const computedStyle = window.getComputedStyle(bgElement);
            extractCssUrls(computedStyle.backgroundImage).forEach(url => {
                addUnique(result.background_images, {
                    url: absolutize(url),
                    element_selector: elementPath(bgElement)
                }, 'url');
            });
        });
    }

    // Extract @font-face URLs from readable stylesheets
    if (includeFonts) {
        const computedStyle = window.getComputedStyle(element);
        result.fonts.family = computedStyle.fontFamily;
        result.fonts.size = computedStyle.fontSize;
        result.fonts.weight = computedStyle.fontWeight;
        result.fonts.style = computedStyle.fontStyle;

        Array.from(document.styleSheets).forEach(sheet => {
            try {
                Array.from(sheet.cssRules || []).forEach(rule => {
                    if (rule.type === CSSRule.FONT_FACE_RULE) {
                        extractCssUrls(rule.style.getPropertyValue('src')).forEach(url => {
                            addUnique(result.fonts.font_faces, {
                                url: absolutize(url, sheet.href || document.baseURI),
                                family: rule.style.getPropertyValue('font-family'),
                                style: rule.style.getPropertyValue('font-style'),
                                weight: rule.style.getPropertyValue('font-weight'),
                                source: sheet.href || 'inline'
                            }, 'url');
                        });
                    }
                });
            }
            catch (e) {}
        });
    }
    
    // Extract videos
    const videos = element.querySelectorAll('video');
    videos.forEach(video => {
        addUnique(result.videos, {
            src: video.src,
            poster: video.poster,
            width: video.videoWidth,
            height: video.videoHeight,
            duration: video.duration,
            sources: Array.from(video.querySelectorAll('source[src]')).map(source => source.src)
        }, 'src');
    });
    
    // Extract audio
    const audios = element.querySelectorAll('audio');
    audios.forEach(audio => {
        addUnique(result.audio, {
            src: audio.src,
            duration: audio.duration,
            sources: Array.from(audio.querySelectorAll('source[src]')).map(source => source.src)
        }, 'src');
    });
    
    // Extract icons (favicon, apple-touch-icon, etc.)
    const iconLinks = document.querySelectorAll('link[rel*="icon"], link[rel="apple-touch-icon"], link[rel="mask-icon"]');
    iconLinks.forEach(link => {
        addUnique(result.icons, {
            href: absolutize(link.href),
            rel: link.rel,
            sizes: link.sizes ? link.sizes.toString() : null,
            type: link.type
        }, 'href');
    });

    document.querySelectorAll('link[rel="preload"][as="image"], link[rel="prefetch"][as="image"]').forEach(link => {
        if (link.href) {
            addUnique(result.images, {
                src: absolutize(link.href),
                alt: '',
                width: 0,
                height: 0,
                loading: '',
                srcset: link.getAttribute('imagesrcset') || '',
                srcset_urls: extractSrcset(link.getAttribute('imagesrcset') || '').map(url => absolutize(url)),
                element_selector: 'link[rel=' + link.rel + '][as=image]'
            }, 'src');
        }
    });

    document.querySelectorAll('meta[property="og:image"], meta[name="twitter:image"]').forEach(meta => {
        const content = meta.getAttribute('content');
        if (content) {
            addUnique(result.images, {
                src: absolutize(content),
                alt: '',
                width: 0,
                height: 0,
                loading: '',
                srcset: '',
                srcset_urls: [],
                element_selector: meta.getAttribute('property') || meta.getAttribute('name')
            }, 'src');
        }
    });

    document.querySelectorAll('link[rel~="stylesheet"][href]').forEach(link => {
        addUnique(result.stylesheets, {
            href: absolutize(link.href),
            media: link.media || '',
            crossorigin: link.crossOrigin || ''
        }, 'href');
    });

    if (window.performance && typeof window.performance.getEntriesByType === 'function') {
        window.performance.getEntriesByType('resource').forEach(entry => {
            addUnique(result.loaded_resources, {
                url: entry.name,
                initiator_type: entry.initiatorType || '',
                transfer_size: entry.transferSize || 0,
                encoded_body_size: entry.encodedBodySize || 0,
                decoded_body_size: entry.decodedBodySize || 0,
                duration: entry.duration || 0
            }, 'url');
        });
    }
    
    return result;
})('$SELECTOR', {
    include_images: $INCLUDE_IMAGES,
    include_backgrounds: $INCLUDE_BACKGROUNDS, 
    include_fonts: $INCLUDE_FONTS,
    fetch_external: $FETCH_EXTERNAL
});
