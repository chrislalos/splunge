# splunge
Splunge is designed to be the world's easiest Python Web framework. Pyramid and Django are fine, but they are not ruthlessly simple.

Splunge is ruthlessly simple. It's not really even a framework. You can write a Web site using splunge, without really using splunge. You can just write the same Python code you'd write anyway.

`splunge` is designed for Python hackers whose focus is on computation and data processing, who then want to make results available on the Web. At present it's not designed for next-gen Web applications, or even database-driven Web apps. But if you process large amounts of data, and want to make it available on the Web, 

## Getting Started

1. `git clone https://github.com/beantaxi/splunge`
2.  `virtualenv --python $(which python3) ~/dev/venv/splunge-test`
3.  `pip install splunge`
4. `cd sample-site`
5. `www`

This will run splunge inside the sample web site - the sample web site will be online!

Some URLs to visit (or curl)
- https://localhost:1313/index.html
- https://localhost:1313/set-underscore
- https://localhost:1313/some-values
- https://localhost:1313/write-to-stdout
- https://localhost:1313/simple-template
- https://localhost:1313/masters-of-models

#### Todo
