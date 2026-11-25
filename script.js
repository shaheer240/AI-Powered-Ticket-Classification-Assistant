const FALLBACK_BASE = "http://127.0.0.1:8000";
const BASES = location.protocol === "file:" ? [FALLBACK_BASE] : ["", FALLBACK_BASE];

const samples = [
  "I placed order #48213 four days ago and the tracking page still says 'label created'. Where is my package?",
  "Please cancel my order 52944, I found the same item cheaper somewhere else.",
  "The courier marked my parcel as delivered but nothing is at my door.",
  "I returned the shoes two weeks ago and still haven't received my refund.",
  "I was charged twice for the same order, please check my payment.",
  "Can you send me the invoice for order #44872? I need it for my company expenses.",
  "I forgot my password and the reset email never arrives.",
  "Please update my phone number in my profile.",
  "The laptop sleeve I received has a broken zipper after one use.",
  "What are your customer service opening hours?"
];

const ticketBox = document.getElementById("ticket");
const sampleSelect = document.getElementById("sample");
const versionSelect = document.getElementById("version");
const simulateSelect = document.getElementById("simulate");
const button = document.getElementById("analyze");
const errorBox = document.getElementById("error");
const resultBox = document.getElementById("result");

samples.forEach((text, i) => {
  const option = document.createElement("option");
  option.value = text;
  option.textContent = `${i + 1}. ${text.slice(0, 50)}...`;
  sampleSelect.appendChild(option);
});

sampleSelect.addEventListener("change", () => {
  if (sampleSelect.value) ticketBox.value = sampleSelect.value;
});

function showError(message) {
  resultBox.hidden = true;
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function showResult(data) {
  errorBox.hidden = true;
  document.getElementById("category").textContent = data.category.replaceAll("_", " ");
  document.getElementById("summary").textContent = data.summary;
  document.getElementById("meta").textContent =
    `Prompt ${data.prompt_version} - ${data.mode} mode - suggestion only, please review`;
  resultBox.hidden = false;
}

function errorMessage(status, body) {
  if (status === 400) return body.detail || "The ticket is empty. Please enter some text.";
  if (status === 422) return "The request was not valid. Check the ticket text and prompt version.";
  if (status === 502) return `The model returned an unusable answer. ${body.detail || ""}`;
  if (status === 503) return `The backend is not available right now. ${body.detail || ""}`;
  return "Something went wrong. Please try again.";
}

async function callApi(payload) {
  const tried = [];
  for (const base of BASES) {
    const url = `${base}/analyze`;
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.status === 404 || res.status === 405) {
        tried.push(`${url || location.origin + url} (HTTP ${res.status})`);
        continue;
      }
      const body = await res.json().catch(() => ({}));
      return { res, body };
    } catch (err) {
      tried.push(`${base || location.origin}/analyze (${err.message})`);
    }
  }
  throw new Error(tried.join("; "));
}

async function analyze() {
  button.disabled = true;
  button.textContent = "Analyzing...";
  const payload = {
    ticket: ticketBox.value,
    prompt_version: versionSelect.value
  };
  if (simulateSelect.value) payload.simulate = simulateSelect.value;

  let reply;
  try {
    reply = await callApi(payload);
  } catch (err) {
    showError(`Cannot reach the API. Tried: ${err.message}. Start the server with "uvicorn api:app --reload" and open http://127.0.0.1:8000`);
    button.disabled = false;
    button.textContent = "Analyze ticket";
    return;
  }

  try {
    if (reply.res.ok) {
      showResult(reply.body);
    } else {
      showError(errorMessage(reply.res.status, reply.body));
    }
  } catch (err) {
    showError(`The page could not display the result: ${err.message}`);
  }
  button.disabled = false;
  button.textContent = "Analyze ticket";
}

button.addEventListener("click", analyze);
