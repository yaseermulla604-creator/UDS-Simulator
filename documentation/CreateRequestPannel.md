# Adding a New Input Element in [CreateRequestPannel](../vanalyzer/src/components/CreateRequestPannel/CreateRequestPannel.svelte)

This guide will walk you through the process of adding a new input element to the project. The input elements are dynamically generated based on the selected SID and are configured in the `constants.js` file.

## 1. Modify the [`constants.js`](../vanalyzer/src/components/CreateRequestPannel/constants.js) File

To add a new input element, you need to modify the `data` object in the `constants.js` file. This object defines the SIDs and the associated fields that will appear in the form.

### Example Structure of `constants.js`

```javascript
export const data = [
  {
    request: '0x19',
    fields: [
      {
        name: 'Sub Functions',
        type: 'select',
        options: ['0x01', '0x02', '0x03', '0x05', '0x0A', '0x0B', '0x0C', '0x0D', '0x0E', '0x0F', '0x11', '0x12', '0x13', '0x14', '0x15'],
      },
      {
        name: 'Status Mask',
        type: 'checkboxes',
        options: [
          'Status Mask 1',
          'Status Mask 2',
          'Status Mask 3',
          'Status Mask 4',
          'Status Mask 5',
          'Status Mask 6',
          'Status Mask 7',
          'Status Mask 8',
        ],
      },
    ],
  },
  // Other SIDs...
];
```

### Steps to Add a New Input Element

1. **Identify the SID**: Decide under which SID you want to add the new input element. Each SID is represented by a `request` object within the `data` array.

2. **Add the Field Object**: Add a new object to the `fields` array of the desired SID. The object should define the name, type, and options (if applicable) of the new input element.

3. **Input Types**: The `type` field determines how the input will be rendered in the form. Supported input types are:
   - **`select`**: Renders a dropdown menu.
   - **`checkboxes`**: Renders a group of checkboxes.
   - **`text`**: Renders a text input field.

### Example: Adding a Text Input

Suppose you want to add a new text input field under the SID `0x2E`. You would modify the `data` object like this:

```javascript
{
  request: '0x2E',
  fields: [
    { name: 'High Byte', type: 'text' },
    { name: 'Low Byte', type: 'text' },
    { name: 'Data', type: 'text' },
    { name: 'New Field', type: 'text' }, // New text input field
  ],
},
```

### Example: Adding a Select Input

To add a new dropdown (select) input:

```javascript
{
  request: '0x19',
  fields: [
    { name: 'Sub Functions', type: 'select', options: ['0x01', '0x02', '0x03'] },
    { name: 'Status Mask', type: 'checkboxes', options: ['Status Mask 1', 'Status Mask 2'] },
    { name: 'New Select Field', type: 'select', options: ['Option 1', 'Option 2', 'Option 3'] }, // New select input field
  ],
},
```

## 2. Input Types in Detail

### 1. `select`

- **Description**: Renders a dropdown menu that allows users to select one option from a list.
- **Structure**:
  ```javascript
  {
    name: 'Field Name',
    type: 'select',
    options: ['Option 1', 'Option 2', 'Option 3'],
  }
  ```
- **Fields**:
  - `name`: The label of the field.
  - `options`: An array of options that the user can select from.

### 2. `checkboxes`

- **Description**: Renders a group of checkboxes, allowing users to select multiple options.
- **Structure**:
  ```javascript
  {
    name: 'Field Name',
    type: 'checkboxes',
    options: ['Option 1', 'Option 2', 'Option 3'],
  }
  ```
- **Fields**:
  - `name`: The label of the field.
  - `options`: An array of options, each represented by a checkbox.

### 3. `text`

- **Description**: Renders a text input field where users can enter freeform text.
- **Structure**:
  ```javascript
  {
    name: 'Field Name',
    type: 'text',
  }
  ```
- **Fields**:
  - `name`: The label of the field.

## 3. Testing the New Input

After modifying the `constants.js` file, the new input element should automatically appear in the form when the corresponding SID is selected. Ensure to test the new input to verify that it behaves as expected.

## 4. Handling the New Input in `handleSubmit`

In the `handleSubmit` function within your Svelte component, ensure that the new input field is appropriately handled based on its type. For example, you may need to add logic for handling the value of the new field when the form is submitted.

```javascript
function handleSubmit() {
  let result = { sid };
  selectedData.forEach((field) => {
    if (field.type === "select" || field.type === "text") {
      result[field.name] = formData[field.name];
    } else if (field.type === "checkboxes" && hasStatusMask.includes(formData['Sub Functions'])) {
      result[field.name] = formData[field.name]; // Store true/false values directly
    }
  });
  pywebview.api.send_request(result);
  console.log(result);
}
```

By following this guide, you can easily extend the form by adding new input elements, enabling greater flexibility and customization.
```

This documentation provides clear instructions on how to add a new input element, modify the `constants.js` file, and handle different input types in the project.