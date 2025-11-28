document.addEventListener('DOMContentLoaded', function () {
document.querySelectorAll('.seat').forEach(seat => {
  seat.addEventListener('click', () => {
    if (!seat.classList.contains('occupied')) {
      seat.classList.toggle('selected');
    }
  });
});

document.getElementById('booking-form').addEventListener('submit', function(e){
  const selected = document.querySelectorAll('.seat.selected');
  if (selected.length === 0) {
    e.preventDefault();
    alert("Оберіть хоча б одне місце 🎬");
    return;
  }
  selected.forEach(seat => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'selected_seats';
    input.value = seat.dataset.id;
    this.appendChild(input);
  });
});
});