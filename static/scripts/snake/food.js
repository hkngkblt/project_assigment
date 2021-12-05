import { onSnake, expandSnake } from './snake.js'
import { randomGridPosition } from './grid.js'

let food = getRandomFoodPosition()
const EXPANSION_RATE = 1
var characters = 'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ';
var currenCharacter = characters.charAt(Math.floor(Math.random() * characters.length))

export function update() {
  if (onSnake(food)) {
    var soundPath = "static/sounds/snake/" + currenCharacter + ".m4a"
    var audio = new Audio(soundPath)
    audio.play();
    currenCharacter =  characters.charAt(Math.floor(Math.random() * characters.length))
    expandSnake(EXPANSION_RATE)
    food = getRandomFoodPosition()
  }
}

export function draw(gameBoard) {
  const foodElement = document.createElement('div')
  foodElement.textContent = currenCharacter
  
  foodElement.style.textAlign = "center"
  foodElement.style.fontWeight = "bold"
  foodElement.style.gridRowStart = food.y
  foodElement.style.gridColumnStart = food.x
  foodElement.classList.add('food')
  gameBoard.appendChild(foodElement)
}

function getRandomFoodPosition() {
  let newFoodPosition
  while (newFoodPosition == null || onSnake(newFoodPosition)) {
    newFoodPosition = randomGridPosition()
  }
  return newFoodPosition
}