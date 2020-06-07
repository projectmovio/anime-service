from dataclasses import fields


def dataclass_from_dict(dataclass, d):
    try:
        fieldtypes = {f.name: f.type for f in fields(dataclass)}
        print(fieldtypes)
        return dataclass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except:
        return d
