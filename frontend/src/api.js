export async function validateFiles(formData) {
  const res = await fetch("http://localhost:8000/validate", {
    method: "POST",
    body: formData
  });
  return res.json();
}
