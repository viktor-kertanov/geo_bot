from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from config import CLARIFAI_API_KEY
from glob import glob


def clarifai_processor(filename):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)
    metadata = (('authorization', f'Key {CLARIFAI_API_KEY}'),)

    with open(filename, 'rb') as f:
        file_data = f.read()
        image = resources_pb2.Image(base64=file_data)

    request = service_pb2.PostModelOutputsRequest(
        model_id='general-image-recognition',
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(image=image)
             )
        ]
    )

    response = stub.PostModelOutputs(request, metadata=metadata)

    return response


def object_exists_on_img(response, object, min_confidence):
    status_code = response.status.code
    if status_code == status_code_pb2.SUCCESS:
        print(f'Recognition was successful, now starting looking for {object}')
        for concept in response.outputs[0].data.concepts:
            if concept.name == object and concept.value >= min_confidence:
                print(
                    f'We have found {object},\
                     our confidence is: {concept.value:.3%}'
                )
                return True
    else:
        print(f'Some recognition error, status code: {status_code}')
        print(f'Details: {response.outputs[0].status.details}')

    return False


def what_is_on_picture(response, min_confidence):
    status_code = response.status.code
    if status_code == status_code_pb2.SUCCESS:
        print("Recognition was successful.\
        Let's find out what we have on our pictures")

        found_elements = [
            concept for concept in response.outputs[0].data.concepts
            if concept.value >= min_confidence
        ]

        for el_idx, el in enumerate(found_elements, start=1):
            print(
                f"{el_idx}. What: '{el.name.upper()}' :::\
                 Confidence: {el.value: .2%}"
            )

    return found_elements


def process_many_images(images: list[str], min_confidence):
    found = []
    for file in files_aux:
        print(f"\n{'-'*30}\n\nOur current file is {file}\n\n{'-'*30}")
        ai_response = clarifai_processor(file)
        found_names = what_is_on_picture(
            ai_response, min_confidence=min_confidence
        )
        found.append(found_names)

    return found


if __name__ == '__main__':
    files_aux = [
        'data/country_images/afghanistan_position.jpeg',
        'data/country_images/albania_flag.jpeg'
    ]

    folder_path = 'learn_bot/downloads/*.jp*g'
    files_to_process = glob(folder_path)

    a = process_many_images(files_aux, min_confidence=0.95)

    print('Hello Cat!')
