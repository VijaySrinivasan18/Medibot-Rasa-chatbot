import en_pipeline
from typing import Dict, Text, Any, List
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.extractors.extractor import EntityExtractorMixin

# TODO: Correctly register your component with its type
@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR], is_trainable=False
)
class MedicineEntityRecognizer(GraphComponent,EntityExtractorMixin):
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        # TODO: Implement this
        ...

    def train(self, training_data: TrainingData) -> Resource:
        # TODO: Implement this if your component requires training
        pass
        ...


    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # TODO: Implement this if your component augments the training data with
        #       tokens or message features which are used by other components
        #       during training.
        ...
        pass

        # return training_data

    def process(self, messages:List[Message], **kwargs) -> List[Message]:
        """Retrieve the text message, pass it to the classifier
            and append the prediction results to the message class."""
        model=en_pipeline.load()
        # print("Loaded model",model)
        # print("Received Messages type",type(messages))
        for message in messages:
            # print("Process in MedicineEntity server started")
            res=model(message.data["text"])    
            outt=res.ents
            enti="None"
            if len(outt)!=0:
                for i in outt:
                    if i.label_=="MEDICINE_NAME" :
                        enti=str(i)

            entity = {"value": enti,
                    "confidence": None,
                    "entity": "MEDICINE_NAME",
                    "extractor": "MedicineEntityRecognizer"}
            # print("Received entity",entity)
            # message.data['entities'] = entity
            if enti != "None":
                # print("setting recognized entity to message")
                message.set("entities", [entity], add_to_output=True)
        # print("MedicineEntity server completed,final messages ",messages)
        return messages
