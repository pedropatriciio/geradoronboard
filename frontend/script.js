const form = document.getElementById("pptForm");
const statusMessage = document.getElementById("statusMessage");
const submitBtn = document.getElementById("submitBtn");
const comercialSelect = document.getElementById("comercial");
const csSelect = document.getElementById("cs");
const pdfInput = document.getElementById("contrato_pdf");

// ------------------------------
// Carregar colaboradores do backend
// ------------------------------
async function carregarColaboradores() {
  try {
    const response = await fetch("http://localhost:5000/colaboradores");
    const colaboradores = await response.json();

    colaboradores.forEach(pessoa => {
      const option = document.createElement("option");
      option.value = pessoa.nome;
      option.textContent = pessoa.nome;

      if (pessoa.papel.toLowerCase() === "comercial") {
        comercialSelect.appendChild(option.cloneNode(true));
      }

      if (pessoa.papel.toLowerCase() === "cs") {
        csSelect.appendChild(option.cloneNode(true));
      }
    });
  } catch (e) {
    statusMessage.textContent = "Erro ao carregar responsáveis.";
  }
}

document.addEventListener("DOMContentLoaded", carregarColaboradores);

// ------------------------------
// Validação simples do formulário
// ------------------------------
function validarFormulario() {
  submitBtn.disabled = !(
    pdfInput.files.length &&
    comercialSelect.value &&
    csSelect.value
  );
}

pdfInput.addEventListener("change", validarFormulario);
comercialSelect.addEventListener("change", validarFormulario);
csSelect.addEventListener("change", validarFormulario);

// ------------------------------
// Envio do formulário
// ------------------------------
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusMessage.textContent = "Gerando apresentação...";

  submitBtn.disabled = true;

  const formData = new FormData(form);

  try {
    const response = await fetch("http://localhost:5000/generate", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Erro ao gerar PPTX");
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = "Onboarding_CS.pptx";
    document.body.appendChild(a);
    a.click();
    a.remove();

    statusMessage.textContent = "Apresentação gerada com sucesso!";

  } catch (err) {
    statusMessage.textContent = err.message;
  } finally {
    submitBtn.disabled = false;
  }
});