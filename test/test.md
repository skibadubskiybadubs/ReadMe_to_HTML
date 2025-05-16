# Header 1
embedding an image using html with width parameter: <br />
<img src="https://github.com/user-attachments/assets/530d180d-d88e-4198-883f-3fa9c9808ec0" width="400"> <br />

## Header 2
- **bold text**: normal text
- *italic text*: normal text
- ~~crossed text~~: normal text
- <ins>underline text</ins>: normal text
- <sub>subscript</sub>: normal text
- <sup>superscript</sup>: normal text

### Header 3
Quotes:
> **quote 1** quoting
> > **nested quote** nested quote <br />
> **quote 2** another quote <br />
> > and image embeded into a nested quote: <br />
> > ![image](https://github.com/user-attachments/assets/829eb1d6-b457-4fff-a924-5748cb1bdef3 <br />

> A new quote!
> > A new nested quote
> > > Super deeply nested quote

Lists: <br />
1. First list item
   - First nested list item
   - Second nested list item
     - First deep-nested list item
     - Second deep-nested list item
   - Third nested list item
2. Second list item

1. **First item**
   - First-first sub-item
   - First-second sub-item

2. **Second item**
   - Second-first sub-item
   - Second-second sub-item

3. **Third item**
   - Third-first sub-item with `some code` embeding

Tables: <br />
| **Col A**      | **Col B** | **Col C** | **Col D** |
|----------------|-----------|----------------------|-----------------------|
| Row A     | 37        | 5.18222              | 166,500               |
| Row B    | 23        | 4.788554             | 103,500               |
| Row C      | 1         | 0.0227125            | 1,500                 |


#### Header 4
Code snippets: <br />
1. Clone this repository:
   ```bash
   git clone https://github.com/skibadubskiybadubs/ReadMe_to_HTML.git
   cd energyplus-parallel
   ```

```bash
python ReadmeToHTML.py "https://github.com/skibadubskiybadubs/ReadMe_to_HTML/blob/main/test/test.md" "test.html"
```

- `--eplus`: Path to the EnergyPlus installation directory (required)
- `--max-workers`: Maximum number of parallel simulations (default: number of logical processors - 1)
- `--csv`: Output CSV file name (default: "simulation_results.csv")

##### Header 5
Links:
Here is some link [to a cool website](https://mybro.win/).

embedding an image using native Markdown styling:
![image](https://github.com/user-attachments/assets/2e1be662-effa-4af2-ad9b-c659947078e7)
