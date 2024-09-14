function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
      if (page.id === pageId) {
        page.classList.remove('d-none');
      } else {
        page.classList.add('d-none');
      }
    });
  }
  
  // Initialize the app by showing the dashboard
  document.addEventListener('DOMContentLoaded', function () {
    showPage('dashboard');
  });
  
  const rangeInput = document.getElementById('customRange1');
    const rangeLabel = document.getElementById('rangeLabel');

    rangeInput.addEventListener('input', function() {
        const value = rangeInput.value;

        if (value == 0) {
            rangeLabel.textContent = `Belum Dikerjakan (${value}%)`;
        } else if (value > 0 && value < 50) {
            rangeLabel.textContent = `Masih dalam Proses (${value}%)`;
        } else if (value >= 50 && value < 100) {
            rangeLabel.textContent = `Sedang Dikerjakan (${value}%)`;
        } else if (value == 100) {
            rangeLabel.textContent = `Sudah Dikerjakan (${value}%)`;
        }
    });

    function handleOtherOption(selectElement) {
        const otherInputContainer = document.getElementById('otherInputContainer');
        if (selectElement.value === 'other') {
          otherInputContainer.classList.remove('d-none');
        } else {
          otherInputContainer.classList.add('d-none');
        }
      }

      $(document).ready(function() {
        $('#datetimepicker1').flatpickr({
          enableTime: true,
          dateFormat: "Y-m-d H:i", // Format yang disimpan dalam input
          altInput: true,
          altFormat: "l, d F Y, H:i", // Format tampilan user
          time_24hr: true,
          locale: "id"
        });
        $('#datetimepicker2').flatpickr({
          enableTime: true,
          dateFormat: "Y-m-d H:i", // Format yang disimpan dalam input
          altInput: true,
          altFormat: "l, d F Y, H:i", // Format tampilan user
          time_24hr: true,
          locale: "id"
        });
      });

      // Funstcion dan event listener untuk fitur fields
      // Function untuk menambah input field secara dinamis
function addInputFields(count) {
  for (let i = 0; i < count; i++) {
    // Buat div baru untuk field
    const newDiv = document.createElement('div');

    // Set innerHTML sesuai dengan struktur input-group
    newDiv.innerHTML = `
      <div class="input-group">
        <input
          type="text"
          aria-label="Nama barang"
          class="form-control"
          placeholder="Nama barang"
          name="itemName"
          required
        />
        <input
          type="text"
          aria-label="Jumlah"
          class="form-control"
          placeholder="Jumlah"
          name="itemQuantity"
          required
        />
        <button type="submit" class="btn btn-primary">+</button>
      </div>
    `;

    // Tambahkan field baru ke dalam container
    fieldsContainer.appendChild(newDiv);
  }
}

// Event listener untuk tombol "Tambah Field"
addFieldsBtn.addEventListener('click', function (e) {
  e.preventDefault(); // Hindari reload page saat tombol diklik
  const selectedCount = parseInt(selectFields.value);  // Ambil nilai dari dropdown
  const customCount = parseInt(customFieldCount.value); // Ambil nilai dari input custom
  const count = customCount || selectedCount;  // Gunakan nilai custom jika ada, atau dropdown jika tidak
  addInputFields(count);  // Tambahkan field sesuai jumlah yang dipilih
});
