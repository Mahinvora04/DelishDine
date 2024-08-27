const body = document.querySelector("body");
const navbar = document.querySelector(".navbar");
const menuBtn = document.querySelector(".menu-btn");
const cancelBtn = document.querySelector(".cancel-btn");
menuBtn.onclick = () => {
  navbar.classList.add("show");
  menuBtn.classList.add("hide");
  body.classList.add("disabled");
};
cancelBtn.onclick = () => {
  body.classList.remove("disabled");
  navbar.classList.remove("show");
  menuBtn.classList.remove("hide");
};
window.onscroll = () => {
  this.scrollY > 20
    ? navbar.classList.add("sticky")
    : navbar.classList.remove("sticky");
};
feather.replace();

const slider = document.querySelector(".circular-slider");
const image = document.querySelector(".slider .img");
const indicator = document.querySelector(".indicator");
const menuItems = document.querySelectorAll(".menu span");
const description = document.querySelectorAll(".text");
const rotationValues = [-58, -32, 0, 32, 58];
const colors = [
  "radial-gradient(#a74255, #440412)",
  "radial-gradient(#ff4b5f, #a40b16)",
  "radial-gradient(#fdb76d, #f08a00)",
  "radial-gradient(#849ade, #42395f)",
  "radial-gradient(#e7ad59, #883e2a)",
];
const images = ["1", "2", "3", "4", "5"];
let itemIndex = 2;

function rotate(rotationValues) {
  image.style.transform = `rotate(${rotationValues}deg)`;
  indicator.style.transform = `translate(-50%, -50%) rotate(${rotationValues}deg)`;
}
menuItems.forEach((menuItems, i) => {
  menuItems.addEventListener("click", () => {
    image.setAttribute("data-category", i + 1);
    image.style.backgroundImage = `url(/static/Image/img${images[i]}.png)`;
    slider.style.background = colors[i];

    if (i > itemIndex) {
      rotate(rotationValues[itemIndex] - 10);
    } else if (i < itemIndex) {
      rotate(rotationValues[itemIndex] + 10);
    } else {
      return "";
    }
    setTimeout(() => {
      rotate(rotationValues[i]);
    }, 300);
    description.forEach((text) => {
      text.style.display = "none";
    });
    description[i].style.display = "block";
    itemIndex = i;
  });
});

function redirectToRestaurantPage(clickedImage) {
  var categoryValue = clickedImage.getAttribute("data-category");
  var username = document.body.getAttribute("data-user");
  if (categoryValue != null) {
      window.location.href = `/restaurant/${username}/${categoryValue}`;
  } else {
      window.location.href = `/restaurant/takeAway/${username}`;
  }
}

function redirectToTakeAwayPage(clickedRestaurant) {
  var username = document.body.getAttribute("data-user");
  var rest_name = clickedRestaurant.getAttribute("data-title");
  window.location.href = `/take_away/${rest_name}/${username}`;
}

function redirectToBookingPage(){
  var username = document.body.getAttribute("data-user");
  window.location.href = `/restaurant/booking/${username}`;
}

function redirectToBookingRestaurantPage(clickedRestaurant){
  var username = document.body.getAttribute("data-user");
  var rest_name = clickedRestaurant.getAttribute("data-title");
  window.location.href = `/reservation/${rest_name}/${username}`
}


function redirectToProfilePage() {
  var username = document.body.getAttribute("data-user");
  window.location.href = `/profile/${username}`;
}

function redirectToCartPage() {
  var username = document.body.getAttribute("data-user");
  window.location.href = `/cart/${username}`;
}