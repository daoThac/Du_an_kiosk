// Đọc JSON
async function loadData() {
  const response = await fetch("data/benh_ly.json");
  const data = await response.json();
  return data;
}

// Lấy danh sách triệu chứng
async function getSymptoms() {
  const data = await loadData();
  return data.map(item => item["triệu_chứng"]);
}

// Gợi ý theo triệu chứng đã chọn
async function recommend(selected) {
  const data = await loadData();
  return data.filter(item => selected.includes(item["triệu_chứng"]));
}

// Ví dụ chạy thử
getSymptoms().then(symptoms => {
  console.log("Danh sách triệu chứng:", symptoms);
});

recommend(["Sốt", "Ho"]).then(results => {
  console.log("Kết quả gợi ý:", results);
});
