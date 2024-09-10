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
      function addInputFields(count) {
        for (let i = 0; i < count; i++) {
          // Buat div baru untuk input
          const newDiv = document.createElement('div');
          newDiv.classList.add('row', 'mb-1', 'g-0');
      
          // Input Nama Barang
          const nameDiv = document.createElement('div');
          nameDiv.classList.add('col-7');
          const nameInput = document.createElement('input');
          nameInput.type = 'text';
          nameInput.classList.add('form-control');
          nameInput.placeholder = 'Masukkan nama barang';
          nameInput.name = 'itemName';
          nameInput.required = true;
          nameDiv.appendChild(nameInput);
      
          // Input Jumlah Barang
          const quantityDiv = document.createElement('div');
          quantityDiv.classList.add('col-3');
          const quantityInput = document.createElement('input');
          quantityInput.type = 'number';
          quantityInput.classList.add('form-control');
          quantityInput.placeholder = 'Jumlah';
          quantityInput.name = 'itemQuantity';
          quantityInput.required = true;
          quantityDiv.appendChild(quantityInput);
      
          // Tambah button submit di row ini
          const buttonDiv = document.createElement('div');
          buttonDiv.classList.add('col-2');
          const submitBtn = document.createElement('button');
          submitBtn.type = 'submit';
          submitBtn.classList.add('btn', 'btn-primary', 'w-100');
          submitBtn.textContent = 'Tambah ke Daftar';
          buttonDiv.appendChild(submitBtn);
      
          // Gabungkan semua input dan button dalam satu baris
          newDiv.appendChild(nameDiv);
          newDiv.appendChild(quantityDiv);
          newDiv.appendChild(buttonDiv);
      
          // Masukkan ke fieldsContainer
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
