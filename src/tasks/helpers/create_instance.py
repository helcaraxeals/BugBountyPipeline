from python_terraform import *


def return_new_instance(token: str, template: str):
    tf = Terraform()
    tf.init(template)
    ret, stdout, stderr = tf.apply(
        template,
        capture_output=True,
        no_color=IsFlagged,
        skip_plan=True,
        state=f"{template.split('/')[-1]}.tfstate",
        var={'do_token': token})

    if stdout and 'web_ipv4_address' in stdout:
        _, key, value = str(stdout).partition('web_ipv4_address =')
        instance_ip = value.strip()
        return instance_ip
    else:
        return None


def destroy_instance(token: str, template: str):
    tf = Terraform()
    tf.destroy(
        template,
        state=f"{template.split('/')[-1]}.tfstate",
        var={'do_token': token})
