/* provided code starts */
function answerBoxTemplate(title, titleDesc) {
  return `<div class=''>
      <h3 class='episode-title'>${title}</h3>
      <p class='episode-desc'>${titleDesc}</p>
  </div>`
}

function sendFocusTitleIn() {
  document.getElementById("title-in").focus()
}
function sendFocusDescIn() {
  document.getElementById("desc-in").focus()
}

function filterText() {
  document.getElementById("answer-box").innerHTML = ""
  console.log(document.getElementById("title-in").value)
  fetch("/episodes?" + new URLSearchParams({ title: document.getElementById("title-in").value }).toString())
    .then((response) => response.json())
    .then((data) => data.forEach(row => {

      let tempDiv = document.createElement("div")
      tempDiv.innerHTML = answerBoxTemplate(row.title, row.descr)
      document.getElementById("answer-box").appendChild(tempDiv)
    }));

}

function showOtherInput() {
  const selectElement = document.getElementById('genre-options');
  const otherInputElement = document.getElementById('other-genre-input');

  if (selectElement.value === 'other') {
    otherInputElement.style.display = 'block';
  } else {
    otherInputElement.style.display = 'none';
  }
}
/* provided code ends */

function submit(e) {
  e.preventDefault();
  var title = document.getElementById("title-in").value;
  var description = document.getElementById("desc-in").value;
  var genre = document.getElementById("genre-in").value;
  console.log(genre);
  if (genre == "Other") {
    genre = document.getElementById("other-movie-genre").value;
  }
  outDict = { "Title": title, "Description": description, "Genre": genre };
  //send outDict somewhere... where?
  console.log(outDict);

  var songList = [
    {
      title: "7 Years",
      genre: "Pop",
      duration: 237300,
      lyrics: "It's been seven years down the road",
      features: { danceability: 5.66, speechiness: 23, acousticness: 56 }
    },
    {
      title: "6 Years",
      genre: "Pop",
      duration: 237300,
      lyrics: "It's been six years down the road",
      features: { danceability: 53.66, speechiness: 13, acousticness: 60 }
    },
    {
      title: "5 Years",
      genre: "Pop",
      duration: 256900,
      lyrics: "It's been five years down the road",
      features: { danceability: 56.6, speechiness: 43, acousticness: 26 }
    },
    {
      title: "4 Years",
      genre: "Pop",
      duration: 247300,
      lyrics: "It's been four years down the road",
      features: { danceability: 86, speechiness: 43, acousticness: 96 }
    }
  ]

  displayOutput(songList);
}

function displayOutput(songList) {
  var output = document.getElementById("output");
  var rowElements = [];
  var cardElements = [];
  var id = 0;

  for (var song of songList) {
    var c = document.createElement("div");
    c.className = "col-sm-4";
    c.innerHTML = createSongCard(song.title, song.genre, song.duration, song.lyrics, song.features, id);
    cardElements.push(c);
    id++;
  }

  var i = 0;
  while (i < cardElements.length) {
    var row = document.createElement("div");
    row.className = "row";
    row.appendChild(cardElements[i]);
    i++;
    if (i < cardElements.length) {
      row.appendChild(cardElements[i]);
      i++;
    }
    if (i < cardElements.length) {
      row.appendChild(cardElements[i]);
      i++;
    }
    rowElements.push(row);
  }

  for (var row of rowElements) {
    output.appendChild(row);
  }
}

function createSongCard(title, genre, duration, lyrics, features, id) {
  var minute = Math.floor(duration / 1000 / 60);
  var durationText = minute + " minutes and " + Math.floor((duration - minute * 1000 * 60) / 1000) + " seconds";
  var infoCollapseId = "song-info-collapse-" + id;
  var lyricCollapseId = "song-lyric-collapse-" + id;

  return `
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">${title}</h5>
        <h5 class="song-info">
          <span class="genre">${genre} | </span>
          <span class="duration">${durationText}</span>
        </h5>
        <button class="btn btn-primary" type="button" data-toggle="collapse" data-target="#${infoCollapseId}"
          aria-expanded="false" aria-controls=${infoCollapseId}>
          Song Characteristic Details
        </button>
        <div class="collapse song-collapse" id=${infoCollapseId}>
          <div class="card card-body">
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${features.danceability}%" aria-valuemin="0" aria-valuemax="1">
                Danceability
              </div>
            </div>
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${features.speechiness}%" aria-valuemin="0" aria-valuemax="1">
                Speechiness
              </div>
            </div>
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${features.acousticness}%" aria-valuemin="0" aria-valuemax="1">
                Acousticness
              </div>
            </div>
          </div>
        </div>
        <button class="btn btn-primary" type="button" data-toggle="collapse" data-target="#${lyricCollapseId}"
          aria-expanded="false" aria-controls=${lyricCollapseId}>
          Song Lyrics
        </button>
        <div class="collapse song-collapse" id=${lyricCollapseId}>
          <div class="card card-body song-lyric">${lyrics}</div>
        </div>
      </div>
    </div>
  `
}

function reset() {
  document.getElementById("output").innerHTML = "";
}

function initialize() {
  document.getElementById("input-form").addEventListener('submit', submit);
  document.getElementById("input-form").addEventListener('reset', reset);
}
