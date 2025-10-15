const form = document.getElementById('url-form');
const urlInput = document.getElementById('url-input');
const resultsDiv = document.getElementById('results');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const url = urlInput.value;
    resultsDiv.innerHTML = 'Loading...';

    try {
        const response = await fetch(`http://127.0.0.1:8000/checks/?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (data.error) {
            resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            const analysis = data.llm_analysis;
            // Rebuild the entire content of the results div
            resultsDiv.innerHTML = `
                <div id="summary">
                    <h2>Analysis for ${analysis.fonte}</h2>
                    <p><strong>Title:</strong> ${analysis.titulo}</p>
                    <p><strong>Author:</strong> ${analysis.autor || 'N/A'}</p>
                    <p><strong>Publication Date:</strong> ${analysis.data_publicacao || 'N/A'}</p>
                    <p><strong>Main Subjects:</strong></p>
                    <ul>
                        ${analysis.principais_assuntos.map(subject => `<li>${subject}</li>`).join('')}
                    </ul>
                    <p><strong>Summary:</strong> ${analysis.resumo}</p>
                </div>
                <div id="credibility-analysis">
                    <h2>Credibility Analysis</h2>
                    <p><strong>Score:</strong> ${analysis.credibility_score}/10</p>
                    <p><strong>Explanation:</strong> ${analysis.credibility_explanation}</p>
                </div>
            `;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p>An unexpected error occurred: ${error.message}</p>`;
    }
});
