if(console === undefined) var console = { log: function() { } };

$(document).ready(function() {
  var scrolling_display = new ScrollingDisplay();
  setTimeout(function() { scrolling_display.append('<p id="whoa">Whoa<br />Whoa<br />Whoa<br />Whoa'
    + '<br />Whoa</p><p id="ding">Ding</p>'); }, 100);
  setTimeout(function() { scrolling_display.append('<p id="pants">Pants</p>'); }, 500);

  $('.client-name').click(function() {
    console.log(arguments);
    scrolling_display.append('<dl><dt>Pants</dt><dd>No</dd></dl>');
  });

  new TextInflater('.client-name, .channel-name, h1', 1.3);
});


// See http://gsgd.co.uk/sandbox/jquery/easing/ for the jQuery Easing Plugin.
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
    var f = jQuery.easing.happySine;
    var ret = f(x, t, b, c, d);
    //console.log([x, t, b, c, d, ret]);
    //console.log(ret - jQuery.easing.happySine(x, t, b, c, d));
    return ret;
  },

  // Rewritten version of jQuery Easing's easeInOutExpo to make math clearer.
  clearerEaseInOutExpo: function(x, t, b, c, d) {
    var base = 2;
    if(t == 0) return b;                                         // Very start.
    if(t == d) return b + c;                                     // Very end.
    if(x < 1/2) return (1/2)*c*Math.pow(base, 10*(2*x - 1)) + b; // 1st half.
    return (1/2)*c*(-Math.pow(base, -10*(2*x - 1)) + 2) + b;     // 2nd half.
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


function ScrollingDisplay() {
  this._e = $('#details-content');
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
  this._viewport = this._e.parent();
}

ScrollingDisplay.prototype._append_filler = function() {
  var filler = this._get_random_element(this._fillers);
  var html = '';
  $.each(filler, function() {
    html += this + '<br />\n';
  });

  // Put filler text just below visible viewport.
  var y_offset = this._viewport.outerHeight() - this._calculate_preceding_content_height();
  this._e.append('<p class="filler" style="margin-top: ' + y_offset + 'px">' + html + '</p>');
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

ScrollingDisplay.prototype._get_final_filler = function() {
  return this._e.find('.filler:last');
}

// Returns height of all children within containing element.
ScrollingDisplay.prototype._calculate_preceding_content_height = function() {
  var final_filler = this._get_final_filler();
  var elements = (final_filler.size() > 0) ? final_filler.nextAll() : this._e.children();

  var height_sum = 0;
  elements.each(function() {
    height_sum += $(this).outerHeight();
  });
  return height_sum;
}

ScrollingDisplay.prototype.append = function(html) {
  var filler_length = this._append_filler().length;
  this._e.append(html);

  var margin_top = parseInt(this._e.css('marginTop'), 10);
  var final_filler = this._get_final_filler();
  // When using a custom font via CSS font-face, final_filler.outerHeight()'s value will be for the
  // default font rather than the custom one, as there is a delay while the browser loads the font
  // on the order of 50-100 ms. This delay persists even if the browser is loading the font from the
  // local filesystem (during local testing) or from the cache. The only practical way I can see to
  // circumvent this issue is to avoid using a custom font, for though one can insert a setTimeout
  // call that performs the height calculation and animation after a given delay, providing the
  // browser time to load the font, the time to load the font varies on myriad factors.
  //
  // final_filler.offset().top: y coordinate of top of filler block within this._e. Note that this
  //                            value includes the offset of the container itself, which is why we
  //                            must subtract.
  // final_filler.outerHeight(): height of filler, including borders and padding.
  margin_top -= (final_filler.offset().top - this._viewport.offset().top) + final_filler.outerHeight();

  var self = this;
  this._e.animate({
    marginTop: margin_top + 'px'
  }, {
    easing: 'logger',
    duration: 100*filler_length,
    complete: function() {
      console.log('done');
      // Remove newly-invisible elements from DOM.
      var invisible = self._get_final_filler().prevAll().andSelf();
      // BUG: things get messed up if animation is already in progress and I remove elements. Skip
      // removing elements until fixed.
      return;
      invisible.remove();
      self._e.css('marginTop', '0px');
    }
  });
}


function TextInflater(elements, factor) {
  var self = this;
  $(elements).hover(function() {
    var element = $(this);
    // We must store the base_font_size, as if we simply fetch the font size on each hover event,
    // then bad things happen when a resizing animation is triggered while a previous one is still
    // in progress (i.e., the user hovers over the element, moves his mouse out, then quickly hovers
    // over it again). In such a case, the element's font size will be in flux because the resizing
    // animation will still be adjusting it step-by-step, resulting in the font size ending up at a
    // value different from before any animations were triggered.
    if(element.data('base_font_size') === undefined)
      element.data('base_font_size', parseInt(element.css('fontSize'), 10));
    self._adjust_size(element, factor);
  }, function() {
    self._adjust_size($(this), 1);
  });
}

TextInflater.prototype._adjust_size = function(element, factor) {
  element.animate({
    fontSize: factor*element.data('base_font_size')
  }, {
    easing: 'logger',
    duration: 200
  });
}
