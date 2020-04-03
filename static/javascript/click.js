function everywhereshow(){
            imgArr=[ '../static/images/kkk.jpg' , '../static/images/bbk.jpg' , '../static/images/bb.jpg' , '../static/images/fff.jpg' , '../static/images/jjj.jpg' ,'../static/images/mm.jpg' ];
            var index =parseInt(Math.random()*(imgArr.length-1));          
            var currentImage=imgArr[index];
            document.getElementById("pp").style.backgroundImage="url("+currentImage+")";
}
