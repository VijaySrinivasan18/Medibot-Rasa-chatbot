class Chatbox {
    
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            uploadButton: document.querySelector('.upload__button')
        }


        this.state = false;
        this.messages = [];
        this.img=[]
    }



    display() {
        const {openButton, chatBox, sendButton,uploadButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        uploadButton.addEventListener("click",() => this.onuploadButton(chatBox))



        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: "You: "+text1 }
        this.messages.push(msg1);

        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "Medibot", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
          });
    }

    onuploadButton(chatbox){
        // var uploaded=chatbox.querySelector("#img_input")
        const uploaded=document.getElementById("img_input")
        if (uploaded.value==="")
        {console.log("Nothing entered") }

        // console.log((uploaded.value))
        
        let file=uploaded.files[0];
        let reader=new FileReader();

        reader.addEventListener("load",()=>{

            let msg1 = { name: "User", message: "Image uploading" }
            this.messages.push(msg1);
    
            fetch('http://127.0.0.1:5000/img', {
                method: 'POST',
                // body: JSON.parse({message:reader.result}),
                body: JSON.stringify({ message: reader.result }),
                mode: 'cors',
                headers: {
                  'Content-Type': 'application/json'
                },
              })
              .then(r => r.json())
              .then(r => {
                let msg2 = { name: "Medibot", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(chatbox)
                textField.value = ''
    
            }).catch((error) => {
                console.error('Error:', error);
                this.updateChatText(chatbox)
                textField.value = ''
              });
        
        
        
        });

        reader.readAsDataURL(file); 
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Medibot")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}



const chatbox = new Chatbox();
chatbox.display();


















_________________________________________________________

// class Chatbox{
//     constructor(){

//         this.args={

//             openButton: document.querySelector(selectors:'.chatbox__button'),
//             chatBox: document.querySelector(selectors:'chatbox__support'),
//             sendbuton: document.querySelector(selectors:'send__button')
//         }

//         this.state=false;
//         this.message=[];

//     }

//     display(){

//         const {openButton,chatBox,sendButton}=this.args;
//         openButton.addEventListener(type:'click',listener:()=>this.toggleState(chatBox))
//         sendButton.addEventListener(type:'click',listener:()=>this.onSendButton(chatBox))
//         const  node = chatBox.querySelector(selectors:'input');
//         node.addEventListener(type:"keyup",listener:({key:string}) => {

//             if (key==="Enter"){
//                 this.onSendButton(chatBox)
//             }
//         })
//     }

//     toggleState(chatbox) {

//         this.state=!this.state;

//         if(this.state){
//             chatbox.classList.add('chatbox--active')
//         } else{
//             chatbox.classList.remove(tokens:'chatbox--activate')
//         }

//     }

//     onSendButton(chatbox){
//         var textField= chatbox.querySelector('input');
//         let text1 = textField.value
//         if (text1===""){
//             return ;
//         }
//         let msg1={name:"User",message:text1}
//         this.message.push(msg1);
//         // 'http://127.0.0.1:5000/predict'
//         fetch(input: $SCRIPT_ROOT+'/predict', init:{
//             method: 'POST',
//             body: JSON.stringify(value:{ message: text1 }),
//             mode: 'cors',
//             headers: {
//               'Content-Type': 'application/json'
//             },
//           })
//           .then(r => r.json())
//           .then(r => {
//             let msg2 = { name: "Medi_Bot", message: r.answer };
//             this.messages.push(msg2);
//             this.updateChatText(chatbox)
//             textField.value = ''

//         }).catch((error) => {
//             console.error('Error:', error);
//             this.updateChatText(chatbox)
//             textField.value = ''
//           });
//     }

//     updateChatText(chatbox) {
//         var html = '';
//         this.messages.slice().reverse().forEach(function(item, index:number) {
//             if (item.name === "Medi_Bot")
//             {
//                 html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
//             }
//             else
//             {
//                 html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
//             }
//           });

//         const chatmessage = chatbox.querySelector('.chatbox__messages');
//         chatmessage.innerHTML = html;
//     }

// }

// const chatbox = new Chatbox();
// chatbox.display();
