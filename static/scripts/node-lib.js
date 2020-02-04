const delay = ms => new Promise(res => setTimeout(res, ms));
            
var nodeCount = 0;
var linkCount = 0;
var humanCount = 0;

class NetLinker {
    get element() {
        return this._element;
    }

    get thickness() {
        return this._thickness;
    }
    set thickness(value) {
        this._thickness = value;
        this._refresh();
    }

    constructor(pointA, pointB) {
        this._origin = pointA;
        this._dest = pointB;
        pointA._links.push(this);
        pointB._links.push(this);
        this._num = linkCount.toString();
        this._thickness = 16;
        this._x = this._origin.x - this._thickness / 2;
        this._y = this._origin.y;
        this._dx = this._dest.x - this._thickness / 2;
        this._dy = this._dest.y;
        this._length = Math.sqrt(Math.pow(this._x - this._dx, 2) + Math.pow(this._y - this._dy, 2));
        this._rotation = Math.atan((this._y - this._dy) / (this._x - this._dx)) * 180 / Math.PI;
        let code = '<rect id="link' + this._num + '" class="link" x="' + this._x.toString() + '" y="' + this._y.toString() + '" width="' + this._thickness.toString() + '" height="' + this._length.toString() + '" style="fill:#888;transform-origin:' + (this._x + this._thickness / 2).toString() + 'px ' + this._y.toString() + 'px" transform="rotate(' + (this._rotation - 90).toString() + ')"></rect>';
        canvas = document.getElementById("canvas");
        canvas.insertAdjacentHTML("afterbegin", code);
        this._element = document.getElementById("link" + this._num);
        linkCount++;
    }

    queryPoint(node) {
        if (node == this._origin) {
            return 1;
        } else if (node == this._dest) {
            return 2;
        } else {
            return 0;
        }
    }

    async sendMessage(from) {

    }

    _refresh() {
        this._x = this._origin.x - this._thickness / 2;
        this._y = this._origin.y;
        this._dx = this._dest.x - this._thickness / 2;
        this._dy = this._dest.y;
        this._length = Math.sqrt(Math.pow(this._x - this._dx, 2) + Math.pow(this._y - this._dy, 2));
        this._rotation = Math.atan((this._y - this._dy) / (this._x - this._dx)) * 180 / Math.PI;
        this.element.setAttribute("x", this._x.toString());
        this.element.setAttribute("y", this._y.toString());
        this.element.setAttribute("width", this._thickness.toString());
        this.element.setAttribute("height", this._length.toString());
        this.element.setAttribute("style", 'fill:#888;transform-origin:' + (this._x + this._thickness / 2).toString() + 'px ' + this._y.toString() + 'px');
        this.element.setAttribute("transform", 'rotate(' + (this._rotation - 90).toString() + ')');
    }
}

class NetNode {
    get element() {
        return this._element;
    }

    get x() {
        return this._x;
    }
    set x(value) {
        this._x = value;
        this._refresh();
    }
    get y() {
        return this._y;
    }
    set y(value) {
        this._y = value;
        this._refresh();
    }

    get size() {
        return this._size;
    }
    set size(value) {
        this._size = value;
        this._refresh();
    }

    get colour() {
        return this._colour;
    }
    set colour(value) {
        this._colour = value;
        this._refresh();
    }

    _refresh() {
        this.element.setAttribute("transform", 'scale(' + this._size.toString() + ') translate(' + this._x.toString() + ',' + this._y.toString() + ')');
        this.element.setAttribute("style", 'fill:' + this._colour + ';transform-origin:' + this._x.toString() + 'px ' + this._y.toString() + 'px');
        for (let i = 0; i < this._links.length; i++) {
            this._links[i]._refresh();
        }
    }

    constructor(x, y, size, colour, responsive=true, debug=true) {
        this._x = x;
        this._y = y;
        this._size = size;
        this._colour = colour;
        this._num = nodeCount.toString();
        this._links = [];
        this.responsive = responsive;
        this.debug = debug;
        canvas = document.getElementById("canvas");
        canvas.insertAdjacentHTML("beforeend", '<g id="node' + nodeCount.toString() + '" class="node" style="fill:' + colour + ';transform-origin:' + x.toString() + 'px ' + y.toString() + 'px" transform="scale(' + size.toString() + ') translate(' + x.toString() + ',' + y.toString() + ')"><circle r="1" class="outer1"></circle><circle r="1" class="outer2"></circle><circle r="1"></circle></g>');
        this._element = document.getElementById("node" + this._num);
        nodeCount++;
    }

    async sendMessage(link, message) {
        await link.sendMessage(this);
        let pointID = link.queryPoint(this);
        if (pointID == 1) {
            return link._dest._onMessage(link, message);
        } else if (pointID == 2) {
            return link._origin._onMessage(link, message);
        } else {
            throw "This node is not on the provided link!";
        }
    }

    async _onMessage(link, message) {
        if (this.responsive) {
            this.size++;
            link.thickness++;
        }
        if (this.debug) {
            console.log("Message received: " + message.toString());
        }
        return await this.onMessage(link, message);
    }

    async onMessage(link, message) {

    }
}

class DumbHuman {
    get element() {
        return this._element;
    }

    get x() {
        return this._x;
    }
    set x(value) {
        this._x = value;
        this._refresh();
    }
    get y() {
        return this._y;
    }
    set y(value) {
        this._y = value;
        this._refresh();
    }

    get size() {
        return this._size;
    }
    set size(value) {
        this._size = value;
        this._refresh();
    }

    get colour() {
        return this._colour;
    }
    set colour(value) {
        this._colour = value;
        this._refresh();
    }

    constructor(x, y, size, message, colour="#808080", debug=true) {
        this._x = x;
        this._y = y;
        this._size = size;
        this._colour = colour;
        this._num = humanCount.toString();
        this._links = [];
        this.message = message;
        this.debug = debug;
        let canvas = document.getElementById("canvas");
        canvas.insertAdjacentHTML("beforeend", '<g id="human' + humanCount.toString() + '" class="human" style="fill:' + colour + ';transform-origin:' + x.toString() + 'px ' + y.toString() + 'px" transform="scale(' + size.toString() + ') translate(' + x.toString() + ',' + y.toString() + ')"><circle r="1" class="outer"></circle><circle r="1"></circle></g>');
        this._element = document.getElementById("human" + this._num);
        this.element.addEventListener('click', e => {console.log(this);this.onclick(this, e);});
        humanCount++;
    }
    _refresh() {
        this.element.setAttribute("transform", 'scale(' + this._size.toString() + ') translate(' + this._x.toString() + ',' + this._y.toString() + ')');
        this.element.setAttribute("style", 'fill:' + this._colour + ';transform-origin:' + this._x.toString() + 'px ' + this._y.toString() + 'px');
        for (let i = 0; i < this._links.length; i++) {
            this._links[i]._refresh();
        }
    }
    async sendMessage(link) {
        await link.sendMessage(this);
        let pointID = link.queryPoint(this);
        if (pointID == 1) {
            return link._dest._onMessage(link, this.message);
        } else if (pointID == 2) {
            return link._origin._onMessage(link, this.message);
        } else {
            throw "This node is not on the provided link!";
        }
    }

    async _onMessage() {

    }

    onclick(self, e) {
        for (let i=0; i < self._links.length; i++) {
            self.sendMessage(self._links[i]);
            console.log("Relayed message '" + self.message.toString() + "' to _links[" + i.toString() + "].");
        }
        console.log("hi.");
    }
}