/* provided code starts */
function answerBoxTemplate(title, titleDesc) {
  return `<div class=''>
      <h3 class='episode-title'>${title}</h3>
  </div>`
}

function sendFocusTitleIn() {
  document.getElementById("title-in").focus()
}
function sendFocusYearIn() {
  document.getElementById("year-in").focus()
}

function filterText() {
  document.getElementById("answer-box").innerHTML = ""
  console.log(document.getElementById("title-in").value)
  fetch("/episodes?" + new URLSearchParams({ title: document.getElementById("title-in").value }).toString())
    .then((response) => response.json())
    .then((data) => data.forEach(row => {

      let tempDiv = document.createElement("div")
      tempDiv.innerHTML = answerBoxTemplate(row.title, row.desc)
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
  var year = document.getElementById("year-in").value;
  var genre = document.getElementById("genre-in").value;
  var emptyTitleError = document.getElementById('empty-input-title-error');
  var emptyGenreError = document.getElementById('empty-input-genre-error');

  if (genre == "Other") {
    genre = document.getElementById("other-movie-genre").value;
  }

  if (genre == 'Select a genre' || genre == "" || title == "") {
    if (genre == 'Select a genre' || genre == "") {
      emptyGenreError.style.display = 'block';
    }
    else {
      emptyGenreError.style.display = 'none';
    }
    if (title == "") {
      emptyTitleError.style.display = 'block';
    }
    else {
      emptyTitleError.style.display = 'none';
    }
    reset()
    return
  }
  else {
    emptyGenreError.style.display = 'none';
    emptyTitleError.style.display = 'none';
  }
  outDict = { "Title": title, "Year": year, "Genre": genre };
  //send outDict somewhere... where?
  console.log(outDict);
  // fetch("/get_output/" + title)
  //   .then((response) => response.json())
  //   .then((data) => {
  //     reset();
  //     displayOutput(data);
  //   })

  if (title == "") {
    title = "a";
  }
  fetch("/get_output/" + title)
    .then((response) => response.json())
    .then((data) => {
      reset();
      displayOutput(data);
    })
}

function displayOutput(songList) {
  var output = document.getElementById("output");
  if (songList.length == 0) {
    var noOutput = document.createElement("div");
    noOutput.innerHTML = "Sorry, we cannot find any relevant result.";
    output.appendChild(noOutput);
    return;
  }

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
  const featureText = featureToText(features)

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
            <p> ${featureText.danceability}</p>
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${features.danceability * 100}%" aria-valuemin="0" aria-valuemax="1">
                Danceability
              </div>
            </div>
            <p> ${featureText.speechiness}</p>
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${features.speechiness * 100}%" aria-valuemin="0" aria-valuemax="1">
                Speechiness
              </div>
              
            </div>
            <p> ${featureText.acousticness}</p>
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${features.acousticness * 100}%" aria-valuemin="0" aria-valuemax="1">
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

function toggleGenreChecks() {
  var checkboxes = document.getElementsByClassName("music-genre");
  var allChecked = document.getElementById("all");
  var checkValue = allChecked.checked ? true : false;

  for (var check of checkboxes) {
    check.checked = checkValue;
  }
}

function toggleCollapseText() {
  var toggleButton = document.getElementById("genreToggleButton");
  if (toggleButton.innerHTML == "Show") {
    toggleButton.innerHTML = "Hide";
  } else {
    toggleButton.innerHTML = "Show";
  }
}

function featureToText(features) {
  let featureText = {}

  if (features.danceability < .5) {
    featureText["danceability"] = "low danceability (score = " + Math.round(features.danceability * 100) + "%)"
  }
  else {
    featureText["danceability"] = "high danceability (score = " + Math.round(features.danceability * 100) + "%)"
  }
  if (features.speechiness < .5) {
    featureText["speechiness"] = "instrumental (score = " + Math.round(features.speechiness * 100) + "%)"
  }
  else {
    featureText["speechiness"] = "lyrical (score = " + Math.round(features.speechiness * 100) + "%)"
  }
  if (features.acousticness < .5) {
    featureText["acousticness"] = "not acoustic (score = " + Math.round(features.acousticness * 100) + "%)"
  }
  else {
    featureText["acousticness"] = "very acoustic (score = " + Math.round(features.acousticness * 100) + "%)"
  }
  return featureText

}


function reset() {
  document.getElementById("output").innerHTML = "";
}

function initialize() {
  document.getElementById("input-form").addEventListener('submit', submit);
  document.getElementById("input-form").addEventListener('reset', reset);
  document.getElementById("all").addEventListener('click', toggleGenreChecks);
  document.getElementById("all").checked = true;
  document.getElementById("genreToggleButton").innerHTML = "Show";
  document.getElementById("genreToggleButton").addEventListener('click', toggleCollapseText);
}
