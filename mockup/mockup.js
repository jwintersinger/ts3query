jQuery.extend(jQuery.easing, {
  // x: Fraction of animation that is complete in range [0, 1). To implement linear easing, simply
  //     return x. Value is t/d.
  // t: Time in ms. 0 <= t < d.
  // b: Starting value. At least for my use, always seems to be 0.
  // c: delta between start and end values. At least for my use, always seems to be 1.
  // d: total length of animation in ms.
  //
  // Return: computed value for current animation. b <= computed value <= b + c.
  
  logger: function(x, t, b, c, d) {
    var f = jQuery.easing.happySwing;
    var ret = f(x, t, b, c, d);
    console.log([x, t, b, c, d, ret]);
    //console.log(ret - jQuery.easing.happySine(x, t, b, c, d));
    return ret;
  },

  // Rewritten version of jQuery Easing's easeInOutExpo to make math clearer.
  clearerEaseInOutExpo: function(x, t, b, c, d) {
    //return jQuery.easing.easeInOutExpo(x, t, b, c, d);
    var base = 2;
    if(t == 0) return b;                                         // Very start.
    if(t == d) return b + c;                                     // Very end.
    if(x < 1/2) return (1/2)*c*Math.pow(base, 10*(2*x - 1)) + b; // 1st half.
    return (1/2)*c*(-Math.pow(base, -10*(2*x - 1)) + 2) + b;     // 2nd half.
  },

  happyPolynomial: function(x, t, b, c, d) {
    var power = 2;
    if(x < 1/2) return Math.pow(x, power);
    return Math.pow(-x + 1, power);
  },

  // Equivalent to jQuery's default jQuery.easing.swing and jQuery Easing's
  // jQuery.easing.easeInOutSine, but I think my version is clearer.
  // I note with some pride that I figured my version out in my head, from scratch, before I
  // compared its output to the two aforementioned alternatives and realized that they were
  // equivalent to mine.
  happySine: function(x, t, b, c, d) {
    return (1/2)*c*(Math.sin(Math.PI*x - Math.PI/2) + 1) + b;
  },
  
  // Copied-and-pasted from jQuery source, with variables renamed but otherwise identical.
  // Note that jQuery Easing plugin overwrites jQuery.easing.swing with a function that simply calls
  // the default easing handler, which the plugin sets to its own easeOutQuad. This caused quite a
  // bit of confusion for me when I tried to find the source of the major discrepancy between my
  // happySwing's output and jQuery's swing.
  happySwing: function(x, t, b, c, d) {
    return ((-Math.cos(x*Math.PI)/2) + 0.5) * c + b;
  }
});

$(document).ready(function() {
  var scrolling_display = new ScrollingDisplay();
  scrolling_display.append('<p id="whoa">Whoa</p>');
  setTimeout(function() { scrolling_display.append('<p id="pants">Pants</p>'); }, 200);
});

function ScrollingDisplay() {
  this._e = $('#weiner');
  this._fillers = [
    'Do you love the good games?',
    'I have a huge bonner.',
    'Huge bonner? More like huge erect phallus.',
    'I just splooged my bonner.',
    'My name is Zoey, and I am so wet.',
    'Oh, baby, you make me moderately damp.',
    'Please me good games.',
    'I spilled beer on my router.'
  ];
}

ScrollingDisplay.prototype._append_filler = function() {
  var filler = this._get_random_element(this._fillers);
  var html = '';
  $.each(filler, function() {
    html += this + '<br />\n';
  });
  this._e.append('<p class="filler" id="pants">' + html + '</p>');
  return filler;
}

ScrollingDisplay.prototype._get_random_element = function(arr) {
  return arr[this._get_random_int(0, arr.length - 1)];
}

// Returns int in [min, max].
// According to https://developer.mozilla.org/En/Core_JavaScript_1.5_Reference/Objects/Math/Random,
// using Math.round will give non-uniform distribution.
ScrollingDisplay.prototype._get_random_int = function(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

ScrollingDisplay.prototype.append = function(html) {
  var filler_length = this._append_filler().length;
  this._e.append(html);

  var margin_top = parseInt(this._e.css('marginTop'), 10);
  var final_filler = this._e.find('.filler:last');
  // When using a custom font via CSS font-face, final_filler.outerHeight()'s value will be for the
  // default font rather than the custom one, as there is a delay while the browser loads the font
  // on the order of 50-100 ms. This delay persists even if the browser is loading the font from the
  // local filesystem (during local testing) or from the cache. The only practical way I can see to
  // circumvent this issue is to avoid using a custom font, for though one can insert a setTimeout
  // call that performs the height calculation and animation after a given delay, providing the
  // browser time to load the font, the time to load the font varies on myriad factors.
  margin_top -= final_filler.outerHeight() + final_filler.offset().top;

  this._e.animate({
    marginTop: margin_top + 'px'
  }, {
    easing: 'logger',
    duration: 100*filler_length,
    complete: function() {
      // TODO: remove invisible from DOM; here, I do nothing with them. Must work out how to stop
      // elements below invisible from being positioned way upward once invisible elements are
      // removed.
      var invisible = $.grep($(this).children(), function(child) {
        var child = $(child);
        if(child.offset().top + child.height() < 0) return true;
      });
    }
  });
}
