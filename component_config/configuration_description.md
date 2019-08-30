### API Key (`#apiKey`)

The API key for the Sendinblue service needs to be obtained from Sendinblue account settings. More information can be found in [the article](https://help.sendinblue.com/hc/en-us/articles/209467485-What-s-an-API-key-and-how-can-I-get-mine-).


### Input table

Multiple input tables can be specified on input. The input table must have 2 mandatory columns, otherwise the execution will fail. The list of allowed columns is following:

- `emailObject` - an array of objects of recipients,
- `templateId` - an id of a template, which will be sent to the recipient,
- `params` - an object of parameters to be appended to the template,
- `ccObject` - an array of objects of recipients to be included in copy,
- `bccObject` - an array of objects of recipients to be included in blind copy.

All of the columns are described in more detailed below.

#### Columns `emailObject`, `ccObject`, `bccObject`

An `emailObject` is a mandatory column, while both `ccObject` and `bccObject` are optional columns and may be left blank or not included at all. All three objects share the same configuration.

All recipients included within a single array will be included in a single email. Each object within the array must consists of mandatory field `email` and optional field `name`. If the mandatory field `email` is missing, the error from Sendinblue API is returned and recorded in the `errors` table. A sample of such object, might look like this:

```
[
    {
        "email": "john@doe.com"
    },
    {
        "email": "testy@mctestface.com",
        "name": "Testy McTestFace"
    }
]
```

which would result in the email being sent to two recipients, whereas the below specification would send email to a single recipient:

```
[
    {
        "email": "john@doe.com"
    }
]
```

#### Column `templateId`

An identification number of the template, which will be sent to specified recipients. If template is not found or active, the error is recorded in `errors` table. The column is mandatory.

#### Column `params`

An optional column to personalize each template. For correct specification of parameters in the template, [follow the official parameters guide](https://help.sendinblue.com/hc/en-us/articles/360000946299-Create-customize-transactional-email-templates). An example of `params` object:

```
{
    "product": "protein",
    "value": "20.00"
}
```