# Displaying and Updating Output Stack in Svelte

This documentation covers the implementation and usage of a Svelte component that interacts with an `outputStack` store to display and update output data.

## Overview

The component imports two reactive stores, `outputStack` and `requestIndex`, and provides functionality to update the `outputStack` and display its current value based on the `requestIndex`.

### Key Features
- **Updating the Output Stack**: A function `updateOutputStack` is defined to append new output data to the `outputStack`.
- **Displaying the Output**: The component dynamically displays the most recent output or a specific indexed output based on `requestIndex`.

## Component Breakdown

### 1. Import Statements

```javascript
import { outputStack, requestIndex } from "../../store/store";
```

- **`outputStack`**: A Svelte store that holds an array of output data.
- **`requestIndex`**: A Svelte store that specifies the index of the output to be displayed.

### 2. Function: `updateOutputStack`

```javascript
function updateOutputStack(newOutput) {
  console.log("Output Stack: ", newOutput);
  outputStack.update((prevOutput) => [...prevOutput, newOutput]);
  console.log($outputStack);
}

window.updateOutputStack = updateOutputStack;
```

- **Purpose**: This function appends `newOutput` to the existing `outputStack`.
- **Usage**: The function is exposed globally via `window.updateOutputStack`, allowing it to be called from outside the Svelte component (e.g., from other JavaScript scripts or external events).

### 3. Reactive Statement for Displaying Output

```javascript
$: {
  const index = $requestIndex;
  if (index === undefined) {
    displayValue = $outputStack[$outputStack.length - 1] || "No data available";
  } else {
    displayValue = $outputStack[index];
  }
}
```

- **`$requestIndex`**: Reactively watches for changes in `requestIndex` to determine which output to display.
- **`displayValue`**: Holds the output data to be displayed. It shows:
  - The last entry in the `outputStack` if `requestIndex` is undefined.
  - The specific entry from `outputStack` at the index specified by `requestIndex`.
  - `"No data available"` if `outputStack` is empty and `requestIndex` is undefined.

### 4. Displaying the Output

```html
<pre>{displayValue}</pre>
```

- **Purpose**: Displays the content of `displayValue` inside a `<pre>` tag for preformatted text output. This allows for easy viewing of the data as-is, with preserved whitespace and formatting.

## How to Use This Component

1. **Updating the Output Stack**: To add new output data, call the `updateOutputStack` function from anywhere in your application:

   ```javascript
   window.updateOutputStack("Your new output data");
   ```

2. **Viewing the Output**:
   - By default, the latest output in the `outputStack` will be displayed.
   - To display a specific output, set the `requestIndex` store to the desired index:

     ```javascript
     requestIndex.set(2); // Displays the third entry in the outputStack
     ```

   - If `requestIndex` is not set, the most recent entry will be displayed.

3. **Example Use Case**:
   - In an application where you process multiple requests and store their outputs, this component helps you keep track of and display each request's output.

## Conclusion

This component provides a simple yet powerful way to manage and display a stack of output data. It allows for both automatic updates with new data and specific data retrieval based on user actions or application state.