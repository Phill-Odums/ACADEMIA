// PDF.js 2-Page Embedded Preview Viewer

class AcademicPDFPreviewViewer {
    constructor(containerId, pdfUrl) {
        this.container = document.getElementById(containerId);
        this.pdfUrl = pdfUrl;
        this.pdfDoc = null;
        this.scale = 1.25;
        this.maxPages = 2; // Strict 2-page preview limit per specification
        this.init();
    }

    async init() {
        if (!this.container || !this.pdfUrl) return;

        // Ensure PDF.js worker is configured
        if (typeof pdfjsLib !== 'undefined') {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        } else {
            console.error('PDF.js library not found');
            return;
        }

        try {
            this.container.innerHTML = `
                <div class="flex flex-col items-center justify-center p-12 text-slate-500">
                    <svg class="animate-spin h-8 w-8 text-indigo-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                    </svg>
                    <p class="text-sm font-medium">Rendering 2-Page Document Preview...</p>
                </div>
            `;

            const loadingTask = pdfjsLib.getDocument({
                url: this.pdfUrl,
                cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/',
                cMapPacked: true
            });

            this.pdfDoc = await loadingTask.promise;
            this.renderAllPages();
        } catch (error) {
            console.error('Error loading PDF:', error);
            this.container.innerHTML = `
                <div class="p-8 text-center bg-rose-50 dark:bg-rose-900/20 rounded-2xl border border-rose-200 dark:border-rose-800">
                    <p class="text-rose-600 dark:text-rose-400 font-semibold mb-1">Unable to display preview</p>
                    <p class="text-xs text-slate-500">The preview document might still be compiling or unavailable.</p>
                </div>
            `;
        }
    }

    async renderAllPages() {
        this.container.innerHTML = '';
        const pagesToRender = Math.min(this.pdfDoc.numPages, this.maxPages);

        for (let pageNum = 1; pageNum <= pagesToRender; pageNum++) {
            const pageWrapper = document.createElement('div');
            pageWrapper.className = 'relative flex flex-col items-center mb-6';

            // Page label badge
            const badge = document.createElement('span');
            badge.className = 'absolute top-3 right-3 z-10 px-2.5 py-1 text-xs font-semibold bg-slate-900/75 backdrop-blur text-white rounded-full';
            badge.textContent = `Page ${pageNum} of 2 (Preview)`;
            pageWrapper.appendChild(badge);

            const canvas = document.createElement('canvas');
            canvas.className = 'pdf-page-canvas shadow-xl border border-slate-200 dark:border-slate-700/60 rounded-xl overflow-hidden bg-white';
            pageWrapper.appendChild(canvas);
            this.container.appendChild(pageWrapper);

            await this.renderPage(pageNum, canvas);
        }

        // Add Watermark End banner
        const endBanner = document.createElement('div');
        endBanner.className = 'w-full text-center py-6 px-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-slate-800 dark:to-slate-800/80 rounded-2xl border border-indigo-100 dark:border-slate-700 mt-2';
        endBanner.innerHTML = `
            <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 mb-2">
                <i data-lucide="lock" class="w-5 h-5"></i>
            </div>
            <h4 class="font-bold text-slate-900 dark:text-white text-sm">End of 2-Page Academic Preview</h4>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">Purchase full access above to unlock and download the complete defended academic project document with code, methodology, findings, and appendices.</p>
        `;
        this.container.appendChild(endBanner);

        if (window.lucide) window.lucide.createIcons();
    }

    async renderPage(num, canvas) {
        const page = await this.pdfDoc.getPage(num);
        const viewport = page.getViewport({ scale: this.scale });
        const context = canvas.getContext('2d');

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        await page.render(renderContext).promise;
    }

    zoomIn() {
        if (this.scale < 2.5) {
            this.scale += 0.2;
            this.renderAllPages();
        }
    }

    zoomOut() {
        if (this.scale > 0.7) {
            this.scale -= 0.2;
            this.renderAllPages();
        }
    }
}

window.AcademicPDFPreviewViewer = AcademicPDFPreviewViewer;
