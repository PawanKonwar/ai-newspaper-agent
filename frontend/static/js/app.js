/**
 * AI Newspaper Agent - Frontend JavaScript
 * Handles form submission, API communication, regenerate, edit, download, and UI updates
 */

class NewspaperAgent {
    constructor() {
        this.form = document.getElementById('articleForm');
        this.topicInput = document.getElementById('topicInput');
        this.wordCountInput = document.getElementById('wordCount');
        this.generateBtn = document.getElementById('generateBtn');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.processingTimeSection = document.getElementById('processingTimeSection');

        this.currentResult = null;
        this.editedFinalContent = null;

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(e);
            });
        }

        if (this.generateBtn) {
            this.generateBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const topic = this.topicInput ? this.topicInput.value.trim() : '';
                const maxLength = this.getMaxLength();
                if (!topic) {
                    this.showAlert('Please enter a topic for your article.', 'warning');
                    return;
                }
                this.generateArticle(topic, maxLength);
            });
        }

        document.querySelectorAll('.word-preset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const words = parseInt(e.target.dataset.words, 10);
                if (this.wordCountInput && !isNaN(words)) this.wordCountInput.value = words;
            });
        });

        const regResearch = document.getElementById('regenerateResearchBtn');
        if (regResearch) regResearch.addEventListener('click', () => this.regenerateResearch());
        const regDraft = document.getElementById('regenerateDraftBtn');
        if (regDraft) regDraft.addEventListener('click', () => this.regenerateDraft());
        const regEdit = document.getElementById('regenerateEditBtn');
        if (regEdit) regEdit.addEventListener('click', () => this.regenerateEdit());

        const editBtn = document.getElementById('editArticleBtn');
        if (editBtn) editBtn.addEventListener('click', () => this.toggleEditArticle());
        const saveBtn = document.getElementById('saveEditedArticleBtn');
        if (saveBtn) saveBtn.addEventListener('click', () => this.saveEditedArticle());
        const cancelBtn = document.getElementById('cancelEditArticleBtn');
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.cancelEditArticle());
        const downloadBtn = document.getElementById('downloadArticleBtn');
        if (downloadBtn) downloadBtn.addEventListener('click', () => this.downloadArticle());

        ['collapseResearch', 'collapseDraft', 'collapseFinal'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('show.bs.collapse', () => this.updateCollapseIcons());
                el.addEventListener('hide.bs.collapse', () => this.updateCollapseIcons());
            }
        });
        this.updateCollapseIcons();
    }

    getMaxLength() {
        if (!this.wordCountInput) return 1200;
        const v = parseInt(this.wordCountInput.value, 10);
        if (isNaN(v)) return 1200;
        if (v < 50) return 50;
        if (v > 5000) return 5000;
        return v;
    }

    async handleFormSubmit(e) {
        if (e && e.preventDefault) e.preventDefault();
        const topic = this.topicInput ? this.topicInput.value.trim() : '';
        const maxLength = this.getMaxLength();
        if (!topic) {
            this.showAlert('Please enter a topic for your article.', 'warning');
            return;
        }
        await this.generateArticle(topic, maxLength);
    }

    async generateArticle(topic, maxLength) {
        try {
            this.showLoadingState();
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, max_length: maxLength })
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const result = await response.json();
            this.hideLoadingState();
            this.currentResult = result;
            this.editedFinalContent = null;
            this.displayResults(result);
        } catch (error) {
            console.error('Error generating article:', error);
            this.hideLoadingState();
            this.showAlert(`Error generating article: ${error.message}`, 'danger');
        }
    }

    showLoadingState() {
        if (this.generateBtn) {
            this.generateBtn.disabled = true;
            this.generateBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Generating...';
        }
        if (this.loadingSection) this.loadingSection.style.display = 'block';
        if (this.resultsSection) this.resultsSection.style.display = 'none';
        if (this.processingTimeSection) this.processingTimeSection.style.display = 'none';
        this.animateProgressBar();
    }

    hideLoadingState() {
        if (this.generateBtn) {
            this.generateBtn.disabled = false;
            this.generateBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Generate Article';
        }
        if (this.loadingSection) this.loadingSection.style.display = 'none';
    }

    animateProgressBar() {
        const progressBar = document.getElementById('progressBar');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
            if (progress >= 90) clearInterval(interval);
        }, 500);
        setTimeout(() => {
            progressBar.style.width = '100%';
        }, 2000);
    }

    displayResults(result) {
        this.updateStageResult('research', result.research_stage);
        this.updateStageResult('draft', result.draft_stage);
        this.updateStageResult('final', result.final_stage);
        this.updateProcessingTime(result.processing_time);
        this.resultsSection.style.display = 'block';
        this.processingTimeSection.style.display = 'block';
        document.getElementById('editArticleArea').style.display = 'none';
        setTimeout(() => {
            this.resultsSection.classList.add('fade-in');
            this.processingTimeSection.classList.add('fade-in');
        }, 100);
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    updateStageResult(stage, stageData) {
        const statusElement = document.getElementById(`${stage}Status`);
        const contentElement = document.getElementById(`${stage}Content`);
        const llmElement = document.getElementById(`${stage}LLM`);

        if (stageData.status === 'success') {
            statusElement.className = 'badge bg-success';
            statusElement.textContent = 'Success';
        } else if (stageData.status === 'error') {
            statusElement.className = 'badge bg-danger';
            statusElement.textContent = 'Error';
        } else {
            statusElement.className = 'badge bg-warning text-dark';
            statusElement.textContent = 'Skipped';
        }

        if (stageData.llm_used) {
            llmElement.textContent = `Powered by ${stageData.llm_used}`;
        }

        const draftWordEl = document.getElementById('draftWordCount');
        const finalWordEl = document.getElementById('finalWordCount');
        if (draftWordEl) {
            if (stage === 'draft' && stageData.word_count != null && stageData.target_word_count != null) {
                draftWordEl.textContent = `Generated: ${stageData.word_count} words (Target: ${stageData.target_word_count})`;
                draftWordEl.style.display = 'block';
            } else if (stage === 'draft') {
                draftWordEl.textContent = '';
                draftWordEl.style.display = 'none';
            }
        }
        if (finalWordEl) {
            if (stage === 'final' && stageData.word_count != null && stageData.target_word_count != null) {
                finalWordEl.textContent = `Generated: ${stageData.word_count} words (Target: ${stageData.target_word_count})`;
                finalWordEl.style.display = 'block';
            } else if (stage === 'final') {
                finalWordEl.textContent = '';
                finalWordEl.style.display = 'none';
            }
        }

        if (stage === 'research') {
            contentElement.innerHTML = this.formatResearchContent(stageData);
        } else if (stage === 'draft') {
            contentElement.innerHTML = this.formatContent(stageData.draft_content || stageData.message);
        } else if (stage === 'final') {
            contentElement.innerHTML = this.formatContent(stageData.final_content || stageData.message);
        }
    }

    formatResearchContent(stageData) {
        const facts = stageData.research_facts;
        if (facts && Array.isArray(facts) && facts.length > 0) {
            let html = '<div class="research-facts">';
            facts.forEach(({ fact, source }) => {
                html += `<div class="research-fact-item mb-2"><span class="fact-text">${this.escapeHtml(fact)}</span> <span class="fact-source badge bg-secondary">Source: ${this.escapeHtml(source)}</span></div>`;
            });
            html += '</div>';
            return html;
        }
        return this.formatContent(stageData.research_data || stageData.message);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatContent(content) {
        if (!content) return '<p class="text-muted">No content available</p>';
        content = this.escapeHtml(content);
        content = content.replace(/\n/g, '<br>');
        return `<div class="article-body">${content}</div>`;
    }

    updateProcessingTime(time) {
        document.getElementById('processingTime').textContent = time ? `${Number(time).toFixed(2)} seconds` : '—';
    }

    async regenerateResearch() {
        if (!this.currentResult) return;
        const topic = this.topicInput.value.trim();
        const maxLength = this.getMaxLength();
        const btn = document.getElementById('regenerateResearchBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Regenerating...';
        try {
            const res = await fetch('/regenerate-research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, max_length: maxLength })
            });
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            this.currentResult.research_stage = data.research_stage;
            this.updateStageResult('research', data.research_stage);
            this.showAlert('Research regenerated. Regenerate Draft to use new research.', 'info');
            document.getElementById('regenerateDraftBtn').focus();
        } catch (e) {
            this.showAlert('Regenerate research failed: ' + e.message, 'danger');
        }
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Regenerate';
    }

    async regenerateDraft() {
        if (!this.currentResult || this.currentResult.research_stage.status !== 'success') {
            this.showAlert('Research must succeed before regenerating draft.', 'warning');
            return;
        }
        const topic = this.topicInput.value.trim();
        const maxLength = this.getMaxLength();
        const research_data = this.currentResult.research_stage.research_data;
        const btn = document.getElementById('regenerateDraftBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Regenerating...';
        try {
            const res = await fetch('/regenerate-draft', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, max_length: maxLength, research_data })
            });
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            this.currentResult.draft_stage = data.draft_stage;
            this.updateStageResult('draft', data.draft_stage);
            if (data.draft_stage.status === 'success') {
                this.showAlert('Draft regenerated. Regenerate Edit to polish the new draft.', 'info');
                document.getElementById('regenerateEditBtn').focus();
            }
        } catch (e) {
            this.showAlert('Regenerate draft failed: ' + e.message, 'danger');
        }
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Regenerate';
    }

    async regenerateEdit() {
        if (!this.currentResult || this.currentResult.draft_stage.status !== 'success') {
            this.showAlert('Draft must succeed before regenerating edit.', 'warning');
            return;
        }
        const topic = this.topicInput.value.trim();
        const draft_content = this.currentResult.draft_stage.draft_content;
        const btn = document.getElementById('regenerateEditBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Regenerating...';
        try {
            const res = await fetch('/regenerate-edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, draft_content })
            });
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            this.currentResult.final_stage = data.final_stage;
            this.editedFinalContent = null;
            this.updateStageResult('final', data.final_stage);
            this.showAlert('Final edit regenerated.', 'success');
        } catch (e) {
            this.showAlert('Regenerate edit failed: ' + e.message, 'danger');
        }
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Regenerate';
    }

    toggleEditArticle() {
        const area = document.getElementById('editArticleArea');
        const textarea = document.getElementById('editArticleTextarea');
        const finalContent = document.getElementById('finalContent');
        if (area.style.display === 'none') {
            const source = this.editedFinalContent != null
                ? this.editedFinalContent
                : (this.currentResult && this.currentResult.final_stage && this.currentResult.final_stage.final_content)
                    ? this.currentResult.final_stage.final_content
                    : '';
            textarea.value = source.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '');
            area.style.display = 'block';
            document.getElementById('editArticleBtn').textContent = 'Hide editor';
        } else {
            area.style.display = 'none';
            document.getElementById('editArticleBtn').textContent = 'Edit Article';
        }
    }

    saveEditedArticle() {
        const textarea = document.getElementById('editArticleTextarea');
        this.editedFinalContent = textarea.value.trim() || null;
        document.getElementById('editArticleArea').style.display = 'none';
        document.getElementById('editArticleBtn').textContent = 'Edit Article';
        if (this.editedFinalContent) {
            const contentEl = document.getElementById('finalContent');
            contentEl.innerHTML = this.formatContent(this.editedFinalContent);
            this.showAlert('Edits saved. Use Download Article to export.', 'success');
        }
    }

    cancelEditArticle() {
        document.getElementById('editArticleArea').style.display = 'none';
        document.getElementById('editArticleBtn').textContent = 'Edit Article';
    }

    downloadArticle() {
        const body = this.editedFinalContent != null
            ? this.editedFinalContent
            : (this.currentResult && this.currentResult.final_stage && this.currentResult.final_stage.final_content)
                ? this.currentResult.final_stage.final_content
                : '';
        if (!body) {
            this.showAlert('No article content to download.', 'warning');
            return;
        }
        const plainBody = body.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '');
        const lines = plainBody.trim().split(/\n+/);
        const headline = lines[0] || 'Untitled Article';
        const wordCount = plainBody.split(/\s+/).filter(Boolean).length;
        const dateGenerated = new Date().toISOString().slice(0, 10);
        const llms = [];
        if (this.currentResult) {
            if (this.currentResult.research_stage.llm_used) llms.push(this.currentResult.research_stage.llm_used);
            if (this.currentResult.draft_stage.llm_used) llms.push(this.currentResult.draft_stage.llm_used);
            if (this.currentResult.final_stage.llm_used) llms.push(this.currentResult.final_stage.llm_used);
        }
        const meta = [
            headline,
            '='.repeat(Math.min(80, headline.length)),
            '',
            `Date generated: ${dateGenerated}`,
            `Word count: ${wordCount}`,
            `LLMs used: ${llms.length ? llms.join(' → ') : 'N/A'}`,
            '',
            '---',
            ''
        ].join('\n');
        const blob = new Blob([meta + plainBody], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `article_${dateGenerated}_${headline.slice(0, 30).replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
        a.click();
        URL.revokeObjectURL(a.href);
        this.showAlert('Article downloaded.', 'success');
    }

    updateCollapseIcons() {
        document.querySelectorAll('.stage-header').forEach(header => {
            const targetId = header.getAttribute('data-bs-target');
            const target = targetId ? document.querySelector(targetId) : null;
            const icon = header.querySelector('.collapse-icon');
            if (icon && target) {
                icon.classList.remove('bi-chevron-down', 'bi-chevron-right');
                icon.classList.add(target.classList.contains('show') ? 'bi-chevron-down' : 'bi-chevron-right', 'me-2', 'collapse-icon');
            }
        });
    }

    showAlert(message, type = 'info') {
        document.querySelectorAll('.alert').forEach(a => a.remove());
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        } else {
            document.body.insertBefore(alertDiv, document.body.firstChild);
        }
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    try {
        window.newspaperAgent = new NewspaperAgent();
    } catch (err) {
        console.error('AI Newspaper Agent init error:', err);
        const btn = document.getElementById('generateBtn');
        if (btn) {
            btn.addEventListener('click', () => {
                alert('Please enter a topic above and try again. If the problem persists, check the browser console (F12) for errors.');
            });
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.getElementById('articleForm');
            if (form) form.dispatchEvent(new Event('submit'));
        }
    });
});
