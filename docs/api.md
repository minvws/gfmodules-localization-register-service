# Searchset
When querying for metadata, the response will contain a Bundle with a type of searchset. The total field will 
contain the number of metadata entries that are available. The entry field will contain a list of metadata entries 
or errors depending on the individual result.
 
## Valid results
If there are valid results, it will be returned within the searchset as another searchset bundle. This bundle 
contains both `ImagingStudy` objects, as well as any related `Patient`, `Practitioner` and `Organization` objects.

The hierarchy of the bundle is as follows:

```
    Bundle: searchset [
        Total: 2
        Entry: [
            Bundle: searchset [
                Total: 7
                Entry [
                    ImagingStudy
                    ImagingStudy
                    ImagingStudy
                    Patient
                    Practitioner1
                    Practitioner2
                    Organization
                ]
            ]
            Bundle: searchset [
                Total: 4
                Entry: [
                    ImagingStudy
                    Patient
                    Practitioner
                    Organization
                ]
            ]
        ]
    ]
```

```
{
  "resourceType": "Bundle",
  "id": "a24f3825-ca45-492c-9427-cfd8ea73a472",
  "type": "searchset",
  "total": 1,
  "entry": [
    {
      "resource": {
        "resourceType": "Bundle",
        "id": "b1dee598-7063-47f0-b633-b9189a6e4c51",
        "type": "searchset",
        "total": 18,
        "entry": [
          {
            "resource": {
              "resourceType": "ImagingStudy",
              "id": "6edc5612-c638-485c-a521-6714bb279dcf",
              "identifier": [
                {
                  "system": "http://example.org/study",
                  "value": "6edc5612-c638-485c-a521-6714bb279dcf"
                }
              ],
              "status": "entered-in-error",
              "subject": {
                "reference": "Patient/7740baa5-466d-4487-a13c-a8d3e7abc450"
              },
              "started": "2023-01-03T09:16:59.057269",
              "numberOfSeries": 3,
              "series": [
                {
                  "uid": "7246d407-3815-4fd7-ba96-995e3af2ba44",
                  "number": 0,
                  "modality": {
                    "coding": [
                      {
                        "system": "http://example.org/modality",
                        "code": "CT",
                        "display": "Digital Radiography"
                      }
                    ]
                  },
                  "bodySite": {
                    "concept": {
                      "coding": [
                        {
                          "system": "http://example.org/body-site",
                          "code": "abdomen",
                          "display": "Chest"
                        }
                      ]
                    }
                  },
                  "started": "2021-08-29T07:58:24.085909",
                  "performer": [
                    {
                      "actor": {
                        "reference": "Practitioner/ff6d3729-fb09-4ada-ac48-58c9618eba2c",
                        "type": "Practitioner"
                      }
                    },
                    {
                      "actor": {
                        "reference": "Organization/6b886e34-771e-4da4-b036-9ec2ee1ed90a",
                        "type": "Organization"
                      }
                    }
                  ],
                  "instance": [
                    {
                      "uid": "ca6c9367-8727-498d-a659-489fccfe0c40",
                      "sopClass": {
                        "system": "http://example.org/sop-class",
                        "code": "MR",
                        "display": "Ultrasound"
                      },
                      "number": 0,
                      "title": "Bijna would bezoek mits hoed gisteren."
                    }
                  ]
                }
              ]
            },
            "search": {
              "mode": "match"
            }
          },
          {
            "resource": {
              "resourceType": "Patient",
              "id": "7740baa5-466d-4487-a13c-a8d3e7abc450",
              "identifier": [
                {
                  "system": "http://example.org/patient",
                  "value": "7740baa5-466d-4487-a13c-a8d3e7abc450"
                }
              ],
              "active": true,
              "name": [
                {
                  "family": "Cosman",
                  "given": [
                    "Benjamin"
                  ]
                }
              ],
              "gender": "male",
              "birthDate": "1978-06-02",
              "address": [
                {
                  "use": "home",
                  "line": [
                    "Bryanstraat 98"
                  ],
                  "city": "Huissen",
                  "postalCode": "4141BO",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Practitioner",
              "id": "ff6d3729-fb09-4ada-ac48-58c9618eba2c",
              "identifier": [
                {
                  "system": "http://example.org/practitioner",
                  "value": "ff6d3729-fb09-4ada-ac48-58c9618eba2c"
                }
              ],
              "active": true,
              "birthDate": "1995-08-14",
              "address": [
                {
                  "use": "work",
                  "line": [
                    "Sterresteeg 63"
                  ],
                  "city": "Werkendam",
                  "postalCode": "2834 MO",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Organization",
              "id": "6b886e34-771e-4da4-b036-9ec2ee1ed90a",
              "identifier": [
                {
                  "system": "http://example.org/org",
                  "value": "6b886e34-771e-4da4-b036-9ec2ee1ed90a"
                }
              ],
              "active": true,
              "type": [
                {
                  "coding": [
                    {
                      "system": "http://example.org/org-type",
                      "code": "pharmacy",
                      "display": "Lab"
                    }
                  ]
                }
              ],
              "name": "Iv-Groep"
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Practitioner",
              "id": "7da08602-3a9b-440e-b186-d506493aaaf3",
              "identifier": [
                {
                  "system": "http://example.org/practitioner",
                  "value": "7da08602-3a9b-440e-b186-d506493aaaf3"
                }
              ],
              "active": true,
              "birthDate": "1989-09-08",
              "address": [
                {
                  "use": "work",
                  "line": [
                    "Matthiasweg 332"
                  ],
                  "city": "Alphen aan den Rijn",
                  "postalCode": "4558 UA",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Practitioner",
              "id": "7658cebc-2ca9-41c0-876b-cb5e89527915",
              "identifier": [
                {
                  "system": "http://example.org/practitioner",
                  "value": "7658cebc-2ca9-41c0-876b-cb5e89527915"
                }
              ],
              "active": true,
              "birthDate": "1909-08-27",
              "address": [
                {
                  "use": "work",
                  "line": [
                    "Lotsingel 98"
                  ],
                  "city": "Wormerveer",
                  "postalCode": "6665 DG",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Practitioner",
              "id": "836dfcb1-1a64-4625-a54a-5e7719ebcae6",
              "identifier": [
                {
                  "system": "http://example.org/practitioner",
                  "value": "836dfcb1-1a64-4625-a54a-5e7719ebcae6"
                }
              ],
              "active": true,
              "birthDate": "1924-11-20",
              "address": [
                {
                  "use": "work",
                  "line": [
                    "Mellestraat 50"
                  ],
                  "city": "Babyloniënbroek",
                  "postalCode": "8516AK",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Patient",
              "id": "13b2306a-f5a0-46a3-9b92-26f47e84b02f",
              "identifier": [
                {
                  "system": "http://example.org/patient",
                  "value": "13b2306a-f5a0-46a3-9b92-26f47e84b02f"
                }
              ],
              "active": true,
              "name": [
                {
                  "family": "le Matelot",
                  "given": [
                    "Sten"
                  ]
                }
              ],
              "gender": "male",
              "birthDate": "2001-02-25",
              "deceasedDateTime": "2024-05-24",
              "address": [
                {
                  "use": "home",
                  "line": [
                    "Marestraat 222"
                  ],
                  "city": "Brandwijk",
                  "postalCode": "8185 ZF",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Practitioner",
              "id": "24d966c3-20d9-44f8-9265-86e9ea5c7b76",
              "identifier": [
                {
                  "system": "http://example.org/practitioner",
                  "value": "24d966c3-20d9-44f8-9265-86e9ea5c7b76"
                }
              ],
              "active": true,
              "birthDate": "1960-09-15",
              "address": [
                {
                  "use": "work",
                  "line": [
                    "Stijnbaan 920"
                  ],
                  "city": "Nunspeet",
                  "postalCode": "7853DJ",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Organization",
              "id": "a8c95062-3261-4d90-9db1-9697b9005c25",
              "identifier": [
                {
                  "system": "http://example.org/org",
                  "value": "a8c95062-3261-4d90-9db1-9697b9005c25"
                }
              ],
              "active": true,
              "type": [
                {
                  "coding": [
                    {
                      "system": "http://example.org/org-type",
                      "code": "pharmacy",
                      "display": "Clinic"
                    }
                  ]
                }
              ],
              "name": "Schenk Tanktransport"
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Practitioner",
              "id": "7644cb77-9bb9-4f8d-aa2d-8256cb7ed72f",
              "identifier": [
                {
                  "system": "http://example.org/practitioner",
                  "value": "7644cb77-9bb9-4f8d-aa2d-8256cb7ed72f"
                }
              ],
              "active": true,
              "birthDate": "1934-03-15",
              "address": [
                {
                  "use": "work",
                  "line": [
                    "Jannestraat 68"
                  ],
                  "city": "Roelofarendsveen",
                  "postalCode": "5331 VB",
                  "country": "Netherlands"
                }
              ]
            },
            "search": {
              "mode": "include"
            }
          },
          {
            "resource": {
              "resourceType": "Organization",
              "id": "9d73f1ff-d810-4bdb-bc26-17a8aa7de0aa",
              "identifier": [
                {
                  "system": "http://example.org/org",
                  "value": "9d73f1ff-d810-4bdb-bc26-17a8aa7de0aa"
                }
              ],
              "active": true,
              "type": [
                {
                  "coding": [
                    {
                      "system": "http://example.org/org-type",
                      "code": "hospital",
                      "display": "Hospital"
                    }
                  ]
                }
              ],
              "name": "van der Schuijt Groep"
            },
            "search": {
              "mode": "include"
            }
          }
        ]
      }
    }
  ]
}

```

## Empty resultset
When no metadata is available for the requested data domain, the response will contain a Bundle with a total of 0.

```
{
  "resourceType": "Bundle",
  "id": "756c9368-1961-486f-94e1-1b72edcb6ed3",
  "type": "searchset",
  "total": 0
}
```

## Error responses

It is possible during the fetching of metadata, that the metadata is not available. In this case, the response 
will contain an OperationOutcome with a severity of error and a code of exception. The details will contain a 
text field with a message that describes the error.

```
{
  "resourceType": "Bundle",
  "id": "7beeb509-7cff-4ab7-bae5-392ab83a51cf",
  "type": "searchset",
  "total": 2,
  "entry": [
    {
      "resource": {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "exception",
            "details": {
              "text": "No addressing found for provider provider_id='123456789' name='ziekenhuis.tilburg@medmij' data_domain=<DataDomain.BeeldBank: 'beeldbank'>"
            }
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "OperationOutcome",
        "issue": [
          {
            "severity": "error",
            "code": "exception",
            "details": {
              "text": "No addressing found for provider provider_id='123456789' name='ziekenhuis.denbosch@medmij' data_domain='beeldbank'"
            }
          }
        ]
      }
    }
  ]
}
```