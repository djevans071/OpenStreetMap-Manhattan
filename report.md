# OpenStreetMap Case Study for Manhattan, NY, USA

For this project, I've chosen to take a look at the island I've been living on for the past eight years: New York County, NY, otherwise known as Manhattan.

![OpenStreetMap Export Tool bounding box](Cover.jpg)

I extracted this data by using OpenStreetMap's Export Tool to manually create a box to be downloaded with Overpass:

```
    (node(40.6983, -74.0242, 40.8816, -73.9054);<;);
    out meta;
```

The limitations of a bounding box prevent me from selecting *only* Manhattan, so bits of the Bronx, Brooklyn, Queens, and New Jersey are going to be included. I will take note of this when I make my SQL queries.


## Initial Issues with Map Data

While I was auditing the data with `audit.py`, I noticed the following anomalies:

 * Misspelling of common street names, like `steet` for `Street` or `Avene` for `Avenue`.
 * Some street names contain whole addresses.
 * The use of alternative street names, most notably `Avenue of the Americas` for `6th Avenue`, or street names like `Lafayette` instead of `Lafayette Street`.
 * Nine digit zip codes like `10001-2062` and zip codes containing letters like `NY 10111`.
 * Invalid zip codes like `100014`, `320`, or `83`

### Inconsistent Street Names
Most inconsistencies in street names are rectified by updating the `mapping` dictionary in `audit.py` and applying a simple renaming module (`update_name` in `audit.py`):

```python
def update_name(name, mapping):
    # update street name if the last word is in the mapping dictionary
    word_list = name.split()
    if word_list[-1] in mapping:
        word_list[-1] = mapping[word_list[-1]]
    name = ' '.join(word_list)
    return name
```
However, some street names are actually inputted as whole addresses like the following:

 ```python
'10024': set(['West 80th Street NYC 10024']),
'NY': set(['405 West 23rd Street, New York, NY',
           '54th W 39th St New York, NY',
           'West 49th Street New York NY']),
'USA': set(['424 5th Avenue, 10018 NY, USA']),
'Unidos': set(['519 9th Ave, New York, NY 10018, Estados Unidos']),
'Uniti': set(['3rd Ave, New York, NY 10028, Stati Uniti'])
 ```

 There are three different ways these addresses are formatted. The address elements are comma separated, spaced separated with `New York` after the address, or space separated with `NYC` after the address. To extract the address only, we modify the `update_name` module as follows:

 ```python
    elif word_list[-1] == '10024':
        ind = name.find('NYC')
        return name[:ind-1]

    # slice address before 'New York' and recursively update the street name
    elif word_list[-1] == 'NY':
        ind = name.find('New York')
        return update_name(name[:ind-1], mapping)

    # take the address before first comma and recursively update street name
    elif word_list[-1] in ['USA', 'Unidos', 'Uniti']:
        street = name.split(',')[0]
        return update_name(street, mapping)
```

### Inconsistent Zip Codes

Things get more interesting with zip codes. Modifying inconsistent zip codes is quite straightforward, as it involves stripping away extraneous characters. More interesting problems crop up when dealing with invalid zip codes. Besides the obviously mistyped `100014`, I found three: `320`, `83`, `97657`. Let us examine them more closely.

First I identify the ids where these zip codes appear, using the following SQL query:

```sql
SELECT *
FROM (SELECT * FROM nodes_tags UNION ALL
      SELECT * FROM ways_tags) tags
WHERE tags.key = 'postcode'
AND (length(tags.value) < 5) OR tags.value = '97657';
```

There are 5 unique ids.
```python
           id       key  value  type
0  1950758029  postcode    320  addr
1   184578578  postcode    320  addr
2   188201723  postcode  97657  addr
3   265347580  postcode     83  addr
4   278366155  postcode     83  addr
```

Using the `get_specific_element` module in `sample.py`, I can pull up the XML entries for those ids.

#### Zip Codes "320" and "97657"

Both entries with zip code `320` have the same basic tags. I've only included the relevant subtags.

```xml
<node changeset="13398343" id="1950758029" lat="40.8524674" lon="-73.9733050" timestamp="2012-10-07T13:55:53Z" uid="714008" user="ubuka0" version="1">
    <tag k="addr:postcode" v="320" />
    <tag k="addr:street" v="Main Street" />
    <tag k="name" v="Fort Lee Public Library" />
</node>
```

The `name` subtag gives it away. The Fort Lee Public Library's address 320 Main Street, Fort Lee, NJ 07024. It looks like the user inputted `320` as the zip code instead of the building number by mistake. The correct zip code for this entry should be `07024`. A special line in `update_zip` makes the appropriate update.

Similarly, the zip code `97657` was mistyped. It is supposed to be `07657`.

#### Zip Code "83"

In this case, there are two different XML entries, each of them are `way` tags. Node subtags are suppressed.

```xml
<way changeset="21017219" id="265347580" timestamp="2014-03-10T00:29:09Z" uid="1764427" user="lxbarth_nycbuildings" version="1">
    <tag k="addr:housenumber" v="830" />
    <tag k="addr:postcode" v="83" />
    <tag k="addr:street" v="5th Avenue" />
    <tag k="building" v="office" />
</way>

<way changeset="41243585" id="278366155" timestamp="2016-08-04T17:57:24Z" uid="40023" user="ALE!" version="5">
    <tag k="addr:housenumber" v="34" />
    <tag k="addr:postcode" v="83" />
    <tag k="addr:street" v="Central Park North" />
    <tag k="name" v="Dana Discovery Center" />
</way>
```

Curiously, both these addresses are located in Central Park. The first is 830 5th Avenue, which on further inspection is the [Arsenal](https://en.wikipedia.org/wiki/Arsenal_(Central_Park), whose zip code is 10065. The second is the Charles Dana Discovery Center which is located on the North side of Central Park at 10029. Zip codes are difficult to determine for Central Park because it's split up into [10 different zip code zones](http://www.zipmap.net/New_York/New_York_County.htm).

![Central Park Zip Zones](CP.jpg)

Updating these zip codes involves modifying the `extract_sec_tags` module in `data.py`.
