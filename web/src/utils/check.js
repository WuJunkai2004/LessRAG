function resCheck(res) {
  if (!res.ok) {
    console.log(res.status);
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

export { resCheck };
