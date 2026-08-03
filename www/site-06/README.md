### site-06: relative imports + absolute imports + subpackages - small site

#### fnf.json

the fnf.json should describe a site with the following
- two child folders
- one grandchild folder
- a relN file and a petname file in each
- a top level hello.py module, a 2nd level hello_2.py module, and a 3rd level hello_3.py module
    - the hello modules are exceptions to the 'each module needs to be imported rule' - they are FORBIDDEN to import
    - each hello module must import a full tree that imports every other non-hello module
    - each hello module must import a rel module from each folder
    - each hello module must import a abs module from each folder
- each non-hello has 0-2 random rel imports of a rel file
- each non-hello has 0-2 random abs imports of a abs file
- each  has a module-level name variable matchin the module name plus a suffix of '-san' (global rule, no need for fnf.json to reflect it)
- imports can and should cross folder boundaries. not all but 70% or so.
- modules named 'relN' get relatively imported
- modules named with petname get absolutely imported
- All folders begin with Capital letters
- All modules begin with lowercase letters

```
{
    "hello": ["rel1", "tiffany", "rel3", "ruger", "rel2", "dolly", "rel4", "ivy"],
    "rel1": ["tiffany"],
    "tiffany": ["dolly"],
    "London_Silly_Nannies": {
        "rel3": ["rel1", "tiffany"],
        "ruger": ["dolly"]
    },
    "Whooping_Street_Wanderers": {
        "hello2": ["rel1", "tiffany", "rel3", "ruger", "rel2", "dolly", "rel4", "ivy"],
        "dolly": ["rel1", "ruger"],
        "rel2": ["rel3", "tiffany"],
        "Boston_Minutemen": {
            "hello3": ["rel1", "tiffany", "rel3", "ruger", "rel2", "dolly", "rel4", "ivy"],
            "rel4": ["rel2", "ruger"],
            "ivy": ["rel4", "dolly"]
        }
    }
}
```
